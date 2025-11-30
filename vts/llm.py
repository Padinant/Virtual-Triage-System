"""
functions relating to connecting the chatbot backend to the frontend, etc
there are two options:
- using openAI SDK (simpler, handles behind the scenes)
- raw https (more control, but also complex)
note this file and the functions in it are as of now, incomplete.
"""

# some libraries we'll possibly use
# unused libraries are commented out so pylint doesn't complain


# import argparse
# import json
# import sys
# import time
# import requests
from openai import OpenAI

from vts.config import load_config

def load_agent_secret_config():
    """
    load the secret config values from the config folder
    precondition: the configuration path exists and contains info in correct format
    """
    cfg = load_config()["agent"]

    # get agent endpoint and api access key from the config file
    endpoint = cfg["url"].rstrip("/") + "/api/v1/"
    access_key = cfg["key"]
    return endpoint, access_key

def ask_agent_openai(input_prompt: str,
                     # ignore unused argument in incomplete function
                     # pylint:disable-next=unused-argument
                     include_retrieval_info: bool = False) -> str:
    """
    this is the main function that does the communication between here and agent
    takes user text as input_prompt and returns the model output as a string
    ignore include_retrieval_info boolean for now
    precondition: the configuration path exists and contains info in correct format
    """
    base_url, key = load_agent_secret_config()

    client = OpenAI(base_url=base_url, api_key=key)

    agent_response = client.chat.completions.create(
        model="n/a",
        messages=[{"role": "user", "content": input_prompt}],
        # # Extra options for later - get meta data on the knowledge base usage:
        # extra_body={
        #     "include_retrieval_info": include_retrieval_info,
        # },
    )

    # Return recieved output (if it exists)
    if agent_response.choices:
        return agent_response.choices[0].message.content

    return "Access to agent failed. Maybe take a look at the FAQ section?"

def create_agent_client():
    """
    creates the agent client
    """
    base_url, key = load_agent_secret_config()
    return OpenAI(base_url=base_url, api_key=key)

def get_agent_response(client, input_prompt: str):
    """
    gets an agent response
    """
    agent_response = client.chat.completions.create(
        model="n/a",
        messages=[{"role": "user", "content": input_prompt}],
        # # Extra options for later - get meta data on the knowledge base usage:
        # extra_body={
        #     "include_retrieval_info": include_retrieval_info,
        # },
    )

    # Return recieved output (if it exists)
    if agent_response.choices:
        return agent_response.choices[0].message.content

    return "Access to agent failed. Maybe take a look at the FAQ section?"

def say_hello_openai() -> str:
    "an example function that can be called at the start!"
    return ask_agent_openai("Say hello and introduce yourself in one short sentence.")

# if this file is ran, have the model introduce itself
if __name__ == "__main__":
    print("Calling on agent to say hello...")
    print(say_hello_openai())
    print("Finished running llm.py")

#########################################################
# other functions - not directly dealing with getting input/output messages
# tbi - to be implemented

# ignore unused arguments on stub
# pylint:disable-next=unused-argument
def update_agent_instruction_prompt(new_instruction_prompt: str) -> bool:
    "tbi"
    return False

# ignore unused arguments on stub
# pylint:disable-next=unused-argument
def add_file_to_kb(new_knowledge_base_file_path: str, kb_id: str) -> bool:
    "tbi"
    return False

# ignore unused arguments on stub
# pylint:disable-next=unused-argument
def create_new_kb(kb_name, kb_decription = ""):
    "tbi; would return the kb api in digital ocean"
    return False

# ignore unused arguments on stub
# pylint:disable-next=unused-argument
def add_kb_to_agent(agent_id: str, kb_id: str):
    "tbi"
    return False
