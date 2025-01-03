import autogen
from autogen import UserProxyAgent
from autogen.agentchat.contrib.captainagent import CaptainAgent
import tempfile
from pathlib import Path
from autogen.coding import CodeBlock, LocalCommandLineCodeExecutor


# Create a temporary directory for code files
temp_dir = tempfile.TemporaryDirectory()

config_path = "OAI_CONFIG_LIST"
config_list = autogen.config_list_from_json(
    config_path
)  # You can modify the filter_dict to select your model

llm_config = {"temperature": 0, "config_list": config_list}

# Set up the Local executor
work_dir = Path("executor_work_dir")
work_dir.mkdir(exist_ok=True)

local_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)

# build agents
captain_agent = CaptainAgent(
    name="captain_agent",
    llm_config=llm_config,
    code_execution_config={"executer": local_executor,
                           "use_docker": False,
                           "last_n_messages": 1},
    agent_config_save_path="captain_agent_configs",  
)


captain_user_proxy = UserProxyAgent(name="captain_user_proxy", 
                                    human_input_mode="ALWAYS",
                                    code_execution_config={"use_docker": False})

USER_QUERY = """
setup docker and home assistant with docker and check if you can use the home assistant api for configuration and management.
Create a short overview of the local Pi
"""

QUERY = f"""YOUR ROLE: You are managing a Raspberry 3 B. 
All USER_QUERIES have to be done on the Raspberry 3 B.
Your main mission is to manage a smart home setup with home assistant.

USER_QUERY: 
{USER_QUERY}

""".strip()

result = captain_user_proxy.initiate_chat(
    captain_agent,
    message=QUERY,
    max_turns=10,
    clear_history=False
)

print("Zwischenstop")

result = captain_user_proxy.initiate_chat(
    captain_agent,
    message="What was our last conversation about?",
    max_turns=2,
    clear_history=False
)
print("Done")