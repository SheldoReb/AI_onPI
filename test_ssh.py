from RemoteCommandLineCodeExecutor import RemoteCommandLineCodeExecutor


remote_executor = RemoteCommandLineCodeExecutor(
    remote_host="192.168.178.18",
    remote_user="ai",
    ssh_key_path=r"C:\Users\Sheldon\.ssh\id_ed25519_remote_ssh",
    ssh_port=22,
    known_hosts_file=r"C:\Users\Sheldon\.ssh\known_hosts",
    allow_unknown_hosts=False,
)

# Test the connection
try:
    if remote_executor.test_connection():
        print("Remote connection is working!")
except RuntimeError as err:
    print(f"Connection test failed: {err}")