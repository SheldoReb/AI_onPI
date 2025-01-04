remote_executor = RemoteCommandLineCodeExecutor(
    remote_host="1.2.3.4",
    remote_user="user",
    ssh_port=22,
    ssh_key_path="/path/to/private_key",
    known_hosts_file="~/.ssh/known_hosts",
    allow_unknown_hosts=False,
)

# Test the connection
try:
    if remote_executor.test_connection():
        print("Remote connection is working!")
except RuntimeError as err:
    print(f"Connection test failed: {err}")