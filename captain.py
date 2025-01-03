import autogen
from autogen import UserProxyAgent
from autogen.agentchat.contrib.captainagent import CaptainAgent
from autogen.coding import DockerCommandLineCodeExecutor
import tempfile

# Create a temporary directory for code files
temp_dir = tempfile.TemporaryDirectory()

config_path = "OAI_CONFIG_LIST"
config_list = autogen.config_list_from_json(
    config_path
)  # You can modify the filter_dict to select your model

llm_config = {"temperature": 0, "config_list": config_list}

# Set up the Docker executor
executor = DockerCommandLineCodeExecutor(
    image="python:3.12-slim",
    timeout=3600,  # Set a long timeout (e.g., 1 hour) to keep the container alive
    work_dir=temp_dir.name,
    stop_container=False  # This flag keeps the container running
)

# build agents
captain_agent = CaptainAgent(
    name="captain_agent",
    llm_config=llm_config,
    code_execution_config={"use_docker": executor},
    agent_config_save_path=None,  # If you'd like to save the created agents in nested chat for further use, specify the save directory here
)
captain_user_proxy = UserProxyAgent(name="captain_user_proxy", human_input_mode="ALWAYS")

USER_QUERY = """
setup home assistant with docker and check if you can use the home assistant api for configuration and management.
"""

QUERY = f"""YOUR ROLE: You are managing a Raspberry 3 B with docker installed. 
All USER_QUERIES have to be done on the Raspberry 3 B.
Your main mission is to manage a smart home setup with home assistant.

USER_QUERY: 
{USER_QUERY}

""".strip()

result = captain_user_proxy.initiate_chat(
    captain_agent,
    message=QUERY,
    max_turns=10,
)


print("Done")
executor.stop()