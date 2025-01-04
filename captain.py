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
)  # You can modify the filter_dict to select your model

llm_config = {"temperature": 0, "config_list": config_list}

# Set up the Docker executor
docker_executor = DockerCommandLineCodeExecutor(
    image="python:3.12-slim",
    timeout=3600,  # Set a long timeout (e.g., 1 hour) to keep the container alive
    work_dir=".",
    stop_container=True,  # This flag keeps the container running
    bind_dir="."
)

# Set up the Local executor
work_dir = Path(".")
work_dir.mkdir(exist_ok=True)

local_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)

# build agents

DESCRIPTION = f"""YOUR ROLE: You are managing a Raspberry 3 B, by building a group of agents at a proper time to solve a task. 
All USER_QUERIES have to be done on the Raspberry 3 B.
Your main mission is to manage a smart home setup with home assistant.
""".strip()

DEFAULT_NESTED_CONFIG = {
    "autobuild_init_config": {
        "config_file_or_env": "OAI_CONFIG_LIST",
        "builder_model": "gpt-4o",
        "agent_model": "gpt-4o",
    },
    "autobuild_build_config": {
        "default_llm_config": {"temperature": 1, "top_p": 0.95, "max_tokens": 2048},
        "code_execution_config": {
            "timeout": 300,
            "work_dir": "groupchat",
            "last_n_messages": 2,
            "use_docker": False,
        },
        "coding": True,
    },
    "group_chat_config": {"max_round": 20},
    "group_chat_llm_config": None,
    "max_turns": 10,
}


captain_agent = CaptainAgent(
    name="captain_agent",
    description=DESCRIPTION,
    llm_config=llm_config,
    nested_config=DEFAULT_NESTED_CONFIG,
    code_execution_config={
                            "executer": docker_executor,
#                           "use_docker": docker_executor,
                           "last_n_messages": 1},
#    agent_config_save_path="captain_agent_configs",
    agent_lib="expert_library/expert_library.json", 
#    tool_lib="tools" 
)


captain_user_proxy = UserProxyAgent(name="captain_user_proxy", 
                                    human_input_mode="ALWAYS",
                                    code_execution_config={"use_docker": docker_executor})

USER_QUERY = """
Lets check if we can configure home assistant via the api on the running container.
lets create the frist user for home assistant via the api, name="Papaja"
""".strip()

result = captain_user_proxy.initiate_chat(
    captain_agent,
    message=USER_QUERY,
    max_turns=10
)

print("Done")