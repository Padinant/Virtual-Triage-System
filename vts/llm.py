"""
functions relating to connecting the chatbot backend to the frontend, etc
there are two options:
- using openAI SDK (simpler, handles behind the scenes) ---> the option we will use
- raw https (more control, but also complex)

note this file and the functions in it are as of now, incomplete.

SOME FUNCTOINS AND CUSTOM TYPES IN THIS FILE THAT YOU MIGHT WANT TO USE:
- ask_agent_openai()         for single prompt questions
- get_agent_response()       for multi-message chats if you have the chat history
- MessageType                the format for passing the chat history in multi-message chats
"""

# from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

from openai import OpenAI

from vts.bot_logging import write_log_entry

from vts.config import load_config

def load_agent_secret_config() -> Tuple[str, str]:
    """
    load the secret config values from the config folder
    precondition: the configuration path exists and contains info in correct format
    """
    cfg = load_config()["agent"]

    # get agent endpoint and api access key from the config file
    endpoint = cfg["url"].rstrip("/") + "/api/v1/"
    access_key = cfg["key"]
    return endpoint, access_key

def ask_agent_openai(input_prompt: str) -> str:
    """
    this is the main function that does the communication between here and agent
    takes user text as input_prompt and returns the model output as a string
    precondition: the configuration path exists and contains info in correct format
    """
    base_url, key = load_agent_secret_config()

    client = OpenAI(base_url=base_url, api_key=key)

    agent_response = client.chat.completions.create(
        model="n/a",
        messages=[{"role": "user", "content": input_prompt}],
    )

    # Return recieved output (if it exists)
    if agent_response.choices:
        return agent_response.choices[0].message.content or ''

    return "Access to agent failed. Maybe take a look at the FAQ section?"

def get_agent_response(client, input_prompt: str):
    """
    gets an agent response
    """
    agent_response = client.chat.completions.create(
        model="n/a",
        messages=[{"role": "user", "content": input_prompt}],
    )

    # Return recieved output (if it exists)
    if agent_response.choices:
        return agent_response.choices[0].message.content

    return "Access to agent failed. Maybe take a look at the FAQ section?"

def say_hello_openai() -> str:
    "an example function that can be called at the start!"
    return ask_agent_openai("Say hello and introduce yourself in one short sentence.")

#########################################################
# NEW PORTION - TO HELP WITH PASSING FULL CHAT HISTORY TO THE MODEL

def get_agent_client() -> OpenAI:
    "this function returns an OpenAI client ready to talk to the DigitalOcean agent."
    base_url, key = load_agent_secret_config()
    return OpenAI(base_url=base_url, api_key=key)

# "Note that the the message type defined below should follow this structure:
# {"role": "user"|"assistant"|"system", "content": "..."}
#
# note a system message might be something the chatbot can see, but
# the user may/may not (such as instruction prompts).
#
# For example, the system message might be: 'You are a helpful
# chatbot. Be polite and brief in your responses.'

MessageType = Dict[str, str]   # {"role": "user"|"assistant"|"system", "content": "..."}

def chat_with_agent(new_message: Optional[str],
                    messages: List[MessageType],
                    stateless: bool=False) -> Tuple[str, List[MessageType]]:
    """
    Call this function if you want to chat to the chatbot, in a way
    that involves multiple back and forths!

    This function sends the full chat history (messages) to the agent
    and returns:
      - assistant_text: the chatbot's reply content
      - updated_messages: original chat history plus the model's
        recent message appended at the end

    if provided, 'new_message' is appended to the end of the messages as a message
    from the "user" role unless 'messages' is empty

    'messages' must be a list of dicts such as:
        {"role": "system", "content": "..."}
        {"role": "user", "content": "..."}
        {"role": "assistant", "content": "..."}

    if 'stateless' is true, then the version without history is used

    note that system is optional; will probably not need to use the "system" role

    Example call:
        msgs = [
            {"role": "assistant", "content": "I'm the UMBC bot, how can I help you?"},
            {"role": "user", "content": "How can I request access to a room on campus?"},
        ]
        reply, msgs = chat_with_agent(msgs)
        print(reply)

    """
    # step 0 - set up key vars
    fail_output_message = "Access to agent failed. Maybe take a look at the FAQ section?"

    # step 1 - get response from the model
    client = get_agent_client()

    # Use the old interface if possible.
    if stateless:
        if new_message:
            return get_agent_response(client, new_message), []
        return "I'm sorry. I didn't understand that.", []

    # A new message is appended before sending.
    if new_message:
        user_message_dict = {"role": "user", "content": new_message}
        updated_messages = messages + [user_message_dict]
    else:
        updated_messages = messages

    resp = client.chat.completions.create(
        model="n/a",
        messages=updated_messages, # type: ignore
    )

    # step 2 - return model reply + the updated history

    if not resp.choices:
        return fail_output_message, updated_messages

    assistant_msg = resp.choices[0].message # ie: what was actually outputted by the model
    assistant_text = ""                     # ie: what we would return as the model reply
    if assistant_msg.content:
        assistant_text = assistant_msg.content
    else:
        assistant_text = fail_output_message

    response_dict = {"role": assistant_msg.role, # the role should be 'assistant'
                     "content": assistant_text}

    updated_messages = updated_messages + [response_dict]

    write_log_entry('test_log.txt', user_message_dict, response_dict)

    return assistant_text, updated_messages

# if this file is ran, have the model introduce itself
if __name__ == "__main__":
    print("Demo 1: Calling on agent to say hello (single prompt)...")
    print(say_hello_openai())
    print("Demo 2: Having a multi-message with agent")
    msgs = [{"role": "system",
             "content": "Say hello and introduce yourself in one short sentence."}]
    reply, msgs = chat_with_agent(None, msgs)
    print("Reply:")
    print(reply)
    print("Messages")
    print(msgs)
    print("Finished running llm.py")
