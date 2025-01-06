import autogen
from autogen import UserProxyAgent
from autogen.agentchat.contrib.captainagent import CaptainAgent
import tempfile
from pathlib import Path
from autogen.coding import CodeBlock, LocalCommandLineCodeExecutor
from autogen.coding import DockerCommandLineCodeExecutor


# Create a temporary directory for code files
temp_dir = tempfile.TemporaryDirectory()

config_path = "OAI_CONFIG_LIST"
config_list = autogen.config_list_from_json(
    config_path
) 

llm_config = {"temperature": 0, "config_list": config_list}


# Set up the Local executor
work_dir = Path("groupchat")
work_dir.mkdir(exist_ok=True)

local_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)

executer = local_executor
use_docker = False

# build agents

DESCRIPTION = f"""YOUR ROLE: You are managing a Raspberry 3 B, by building a group of agents at a proper time to solve a task. 
All USER_QUERIES have to be done on the Raspberry 3 B.
Your main mission is to manage a smart home setup with home assistant.
""".strip()


captain_agent = CaptainAgent(
    name="captain_agent",
#    description=DESCRIPTION,
    llm_config=llm_config,
#    nested_config=DEFAULT_NESTED_CONFIG,
    code_execution_config={
                           "executer": executer,
                           "use_docker": use_docker,
                           "last_n_messages": 1},
#    agent_config_save_path="captain_agent_configs",
    agent_lib="expert_library/expert_library.json", 
    tool_lib="tools" 
)

captain_user_proxy = UserProxyAgent(name="captain_user_proxy", 
                                    human_input_mode="ALWAYS",
                                    code_execution_config={"executer": executer,
                                                           "use_docker": use_docker})

USER_QUERY = """
Get all infos from https://developers.home-assistant.io/docs/api/rest/ use website scraping.
"""
#Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJiMGE0ODNlZjdmZDg0MTE4YTM0ZjJhMDk0OGUxY2QyYiIsImlhdCI6MTczNjA5NTQ3NCwiZXhwIjoyMDUxNDU1NDc0fQ.CPNf9678eeEVcxf01aFjeDr2DyLm3bWgOjDOvQtrAHY
#to check if the token is still valid.
#Then get all configs needed to configure the home assistant.
#""".strip()

result = captain_user_proxy.initiate_chat(
    captain_agent,
    message=USER_QUERY,
    max_turns=10
)

print("Done")