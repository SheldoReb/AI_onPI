import autogen
from autogen import UserProxyAgent


config_path = "OAI_CONFIG_LIST"
config_list = autogen.config_list_from_json(
    config_path
) 

llm_config = {"temperature": 0, "config_list": config_list}


