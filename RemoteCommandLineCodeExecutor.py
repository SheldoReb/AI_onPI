import os
import re
import logging
import paramiko
import tempfile
from hashlib import md5
from typing import ClassVar, List, Optional, Dict, Any
from pathlib import Path

from autogen.code_utils import TIMEOUT_MSG
from autogen.coding.base import CodeExecutor, CodeBlock, CommandLineCodeResult
from autogen.coding.markdown_code_extractor import MarkdownCodeExtractor
from autogen.coding.utils import silence_pip, _get_file_name_from_content

class RemoteCommandLineCodeExecutor(CodeExecutor):
    """
    A 'full permissive' remote code executor that uses Paramiko to SSH into a remote host
    and execute code. Despite being 'full permissive' on the remote side, this example
    performs local sanitization to prevent obviously dangerous commands before sending.
    """

    SUPPORTED_LANGUAGES: ClassVar[List[str]] = [
        "bash",
        "shell",
        "sh",
        "pwsh",
        "powershell",
        "ps1",
        "python",
        "javascript",
        "html",
        "css",
    ]

    def __init__(
        self,
        remote_host: str,
        remote_user: str,
        ssh_port: int = 22,
        ssh_key_path: Optional[str] = None,
        known_hosts_file: Optional[str] = None,
        allow_unknown_hosts: bool = False,
        ssh_options: Optional[Dict[str, Any]] = None,
        timeout: int = 60,
    ):
        """
        Args:
            remote_host (str): The remote hostname or IP.
            remote_user (str): The SSH username.
            ssh_port (int): SSH port (default 22).
            ssh_key_path (Optional[str]): Private key path if using key-based auth.
            known_hosts_file (Optional[str]): Path to a custom known_hosts file.
            allow_unknown_hosts (bool): If True, unknown hosts are accepted automatically.
            ssh_options (Optional[dict]): Additional paramiko SSH flags or settings 
                (e.g., 'compress': True, 'disabled_algorithms': {'pubkeys': ['rsa-sha2-256']}, etc.).
            timeout (int): Execution timeout in seconds.
        """
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.ssh_port = ssh_port
        self.ssh_key_path = ssh_key_path
        self.known_hosts_file = known_hosts_file
        self.allow_unknown_hosts = allow_unknown_hosts
        self.ssh_options = ssh_options or {}
        self._timeout = timeout

        self._ssh_client: Optional[paramiko.SSHClient] = None
        self._sftp_client: Optional[paramiko.SFTPClient] = None

    @property
    def code_extractor(self):
        return MarkdownCodeExtractor()

    @staticmethod
    def sanitize_command(lang: str, code: str) -> None:
        """
        Local sanitization before sending to remote.
        Detect obviously dangerous patterns (e.g. rm -rf).
        Raise ValueError on detection.
        """
        dangerous_patterns = [
            (r"\brm\s+-rf\b", "Use of 'rm -rf' command is not allowed."),
            (r"\bmv\b.*?\s+/dev/null", "Moving files to /dev/null is not allowed."),
            (r"\bdd\b", "Use of 'dd' command is not allowed."),
            (r">\s*/dev/sd[a-z][1-9]?", "Overwriting disk blocks directly is not allowed."),
            (r":\(\)\{\s*:\|\:&\s*\};:", "Fork bombs are not allowed."),
        ]
        if lang in ["bash", "shell", "sh"]:
            for pattern, message in dangerous_patterns:
                if re.search(pattern, code):
                    raise ValueError(f"Potentially dangerous command detected: {message}")

    def _connect_if_necessary(self) -> None:
        """Establish SSH and SFTP connections if not already connected."""
        if self._ssh_client and self._sftp_client:
            return  # Already connected

        # Create Paramiko SSH client and set host key policy
        client = paramiko.SSHClient()

        # If the user provided a known_hosts file, load it
        if self.known_hosts_file:
            client.load_host_keys(self.known_hosts_file)
        else:
            client.load_system_host_keys()

        if self.allow_unknown_hosts:
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        else:
            client.set_missing_host_key_policy(paramiko.RejectPolicy())

        # Additional advanced SSH options can be set here 
        # (disabling algorithms, enabling compression, etc.)
        # Example:
        # if self.ssh_options.get('compress'):
        #     ...
        # paramiko automatically handles many of these, 
        # but you can pass them to connect(**self.ssh_options).

        connect_kwargs = {
            'hostname': self.remote_host,
            'username': self.remote_user,
            'port': self.ssh_port,
            'timeout': self._timeout,
            **self.ssh_options,
        }

        if self.ssh_key_path:
            connect_kwargs['key_filename'] = self.ssh_key_path

        try:
            client.connect(**connect_kwargs)
            self._ssh_client = client
            self._sftp_client = client.open_sftp()
        except Exception as e:
            raise RuntimeError(f"Failed to connect to {self.remote_host}:{self.ssh_port} -> {e}")

    def _disconnect_if_necessary(self) -> None:
        """Close SSH and SFTP if open."""
        if self._sftp_client:
            self._sftp_client.close()
            self._sftp_client = None
        if self._ssh_client:
            self._ssh_client.close()
            self._ssh_client = None

    def execute_code_blocks(self, code_blocks: List[CodeBlock]) -> CommandLineCodeResult:
        """
        Execute code blocks on the remote machine with local sanitization and 
        robust SSH usage (via Paramiko).
        """
        logs_all = ""
        exit_code = 0
        self._connect_if_necessary()  # Ensure we are connected

        try:
            for code_block in code_blocks:
                lang, code = code_block.language.lower(), code_block.code

                # 1) Local sanitization before sending
                self.sanitize_command(lang, code)
                code = silence_pip(code, lang)

                # 2) Generate a remote filename 
                code_hash = md5(code.encode()).hexdigest()
                remote_filename = f"tmp_code_{code_hash}.{lang}"

                # 3) Write to a local temp file, then SFTP to remote
                with tempfile.NamedTemporaryFile("w", delete=False) as tmpf:
                    local_tmp_path = tmpf.name
                    tmpf.write(code)

                try:
                    # Upload the file
                    self._sftp_client.put(local_tmp_path, remote_filename)
                finally:
                    # Clean up local temp file
                    if os.path.exists(local_tmp_path):
                        os.remove(local_tmp_path)

                # 4) Make the file executable (for shell-based code)
                #    Then run it, capturing stdout/stderr.
                cmd_to_run = f"chmod +x {remote_filename} && ./{remote_filename}"

                logs_all += f"\n--- Executing on remote: {remote_filename} ---\n"
                try:
                    # Use SSHClient.exec_command
                    stdin, stdout, stderr = self._ssh_client.exec_command(
                        cmd_to_run, timeout=self._timeout
                    )
                    # Wait for command to complete
                    rc = stdout.channel.recv_exit_status()

                    out_str = stdout.read().decode('utf-8', errors='replace')
                    err_str = stderr.read().decode('utf-8', errors='replace')

                    logs_all += f"STDOUT:\n{out_str}\n"
                    logs_all += f"STDERR:\n{err_str}\n"

                    if rc != 0 and exit_code == 0:
                        exit_code = rc

                except paramiko.SSHException as ssh_ex:
                    logs_all += f"SSH execution error: {ssh_ex}\n"
                    exit_code = 1
                    break
                except Exception as ex:
                    logs_all += f"Unexpected error: {ex}\n"
                    exit_code = 1
                    break
                finally:
                    # Remove the remote file to keep environment clean
                    cleanup_cmd = f"rm -f {remote_filename}"
                    try:
                        self._ssh_client.exec_command(cleanup_cmd)
                    except Exception as e:
                        # If cleanup fails, just log it
                        logs_all += f"(Cleanup failure: {e})\n"

                if exit_code != 0:
                    # If one block fails, we stop.
                    break

        finally:
            # 5) Disconnect if you don't need persistent usage
            self._disconnect_if_necessary()

        return CommandLineCodeResult(exit_code=exit_code, output=logs_all, code_file=None)

    def restart(self) -> None:
        """
        (Optional) You could re-init the SSH session or simply warn that 
        'restart' is not supported. Here we force a reconnect.
        """
        logging.info("Forcing SSH reconnection.")
        self._disconnect_if_necessary()
        self._connect_if_necessary()
    
    def test_connection(self) -> bool:
        """
        Attempt a simple command over SSH to verify connectivity.
        Returns True if the remote command succeeds, otherwise raises an exception.
        """
        self._connect_if_necessary()  # Ensure we are connected
        
        try:
            # Run a harmless command, e.g. `echo "connected"`
            stdin, stdout, stderr = self._ssh_client.exec_command('echo "connected"', timeout=self._timeout)
            rc = stdout.channel.recv_exit_status()
            if rc != 0:
                # If the command failed, we can read stderr for debugging
                error_output = stderr.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"Remote test command failed (exit={rc}): {error_output}")

            # Check output just to confirm we got 'connected'
            output = stdout.read().decode("utf-8", errors="replace")
            if "connected" not in output:
                raise RuntimeError(f"Unexpected output when testing connection: {output}")

            return True
        except Exception as e:
            raise RuntimeError(f"Connection test failed: {e}")
