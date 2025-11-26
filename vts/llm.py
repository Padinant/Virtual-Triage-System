# functions relating to connecting the chatbot backend to the frontend, etc
# there are two options: 
# using openAI SDK (simpler, handles behind the scenes) or via raw https (more control, but also complex)
# note this file and the functions in it are as of now, incomplete.

# some libraries we'll possibly use
import argparse
import configparser
import json
import os
import sys
import time
import requests
from openai import OpenAI


# load the secret config values from the given path
# precondition: the provided file exists and contains info in correct INI format
# returns model endpoint and access key from that file
def load_agent_secret_config(path=".config_ai"):
    cfg = configparser.ConfigParser()
    
    files_read = cfg.read(path)
    if not files_read:
        # something went wrong
        raise FileNotFoundError(f"Something unexpected happened. Config file not found at the path: {path}")
    
    # get agent endpoint and api access key from the given file
    endpoint = cfg.get("agent", "AGENT_ENDPOINT").rstrip("/") + "/api/v1/"
    access_key = cfg.get("agent", "AGENT_API_ACCESS_KEY")
    return endpoint, access_key


# this is the main function that does the communication between here and agent
# takes user text as input_prompt and returns the model output as a string
# ignore include_retrieval_info boolean for now
# precondition: the provided file for config_path exists and contains info in correct INI format
def ask_agent_openai(input_prompt: str, include_retrieval_info: bool = False, config_path: str = ".config_ai") -> str:
    base_url, key = load_agent_secret_config(config_path)

    client = OpenAI(base_url=base_url, api_key=key)

    agent_response = client.chat.completions.create(
        model="n/a",
        messages=[{"role": "user", "content": prompt}],
        # # Extra options for later - get meta data on the knowledge base usage:
        # extra_body={
        #     "include_retrieval_info": include_retrieval_info,
        # },
    )

    # Return recieved output (if it exists)
    if agent_response.choices:
        return agent_response.choices[0].message.content
    else: 
        return ""


# an example function that can be called at the start!
def say_hello_openai() -> str:
    return ask_agent_openai("Say hello and introduce yourself in one short sentence.")




# if this file is ran, have the model introduce itself
if __name__ == "__main__":
    print(say_hello_openai())
