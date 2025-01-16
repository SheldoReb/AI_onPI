import autogen
from autogen import UserProxyAgent
from autogen.agentchat.contrib.captainagent import CaptainAgent
import tempfile
from pathlib import Path
from autogen.coding import CodeBlock, LocalCommandLineCodeExecutor
from autogen.coding import DockerCommandLineCodeExecutor


# Create a temporary directory for code files
temp_dir = tempfile.TemporaryDirectory(dir="groupchat")

config_path = "OAI_CONFIG_LIST"
config_list = autogen.config_list_from_json(
    config_path
) 

llm_config = {"temperature": 0, "config_list": config_list}


# Set up the Local executor
work_dir = temp_dir.name 

local_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)

executer = local_executor
use_docker = False

# build agents

DESCRIPTION = f"""YOUR ROLE: You are managing a Raspberry 3 B, by building a group of agents at a proper time to solve a task. 
All USER_QUERIES have to be done on the Raspberry 3 B.
Your main mission is to manage a smart home setup with home assistant.
Home Assistant is setup up and running on the Raspberry with home assistant OS.
""".strip()

NESTED_CONFIG = {
    "autobuild_init_config": {
        "config_file_or_env": "OAI_CONFIG_LIST",
        "builder_model": "gpt-4o",
        "agent_model": "gpt-4o",
    },
    "autobuild_build_config": {
        "default_llm_config": {"temperature": 1, "top_p": 0.95, "max_tokens": 2048},
        "code_execution_config": {
            "timeout": 300,
            "work_dir": str(work_dir),
            "last_n_messages": 1,
            "use_docker": False,
        },
        "coding": True,
    },
    "group_chat_config": {"max_round": 10},
    "group_chat_llm_config": None,
    "max_turns": 10,
}


captain_agent = CaptainAgent(
    name="captain_agent",
#    description=DESCRIPTION,
    llm_config=llm_config,
    nested_config=NESTED_CONFIG,
    agent_config_save_path="captain_agent_configs",
    agent_lib="expert_library/expert_library.json", 
    tool_lib="tools" 
)

captain_user_proxy = UserProxyAgent(name="captain_user_proxy", 
                                    human_input_mode="ALWAYS")

HA_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIwNTlhZWEyYmYwNDg0ZGZjODQxMTlhMWE2OTg5YjkwOSIsImlhdCI6MTczNjM3MDc1MSwiZXhwIjoyMDUxNzMwNzUxfQ.zj3TL1qGdf7nlYlFaz66H-aLTWsFCS7UMliRlogtGF4"
SHELLYBLU_GATEWAY1="192.168.178.194"

USER_QUERY = """
Use: "https://  developers.home-assistant.io/docs/api/rest/" and env vars: HA_TOKEN, SHELLYBLU_GATEWAY1
Check if you can get the home assistant config from homeassistant api (192.168.178.20:8123)
""".strip()

result = captain_user_proxy.initiate_chat(
    captain_agent,
    message=USER_QUERY,
    max_turns=1,
    clear_history=False,
)
print("Pause")
input("Press Enter to continue...")
USER_QUERY2 = """
Now list all shelly devices in a structured way.
""".strip()
captain_user_proxy.initiate_chat(
    captain_agent,
    message=USER_QUERY,
    max_turns=10,
    clear_history=False,
)

# Clean up the temporary directory after user input confirmation
input("Press Enter to confirm cleanup...")
temp_dir.cleanup()
print("Done")
