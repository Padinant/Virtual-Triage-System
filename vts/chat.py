"""
Internal logic for the backend of the chatbot API.

This is a separate file to keep the website.py part of the chatbot
code as trivial as possible.
"""

from flask import request, jsonify

from markdown_it import MarkdownIt

from vts.chat_server import create_guest_bot

from vts.config import ConfigPathError, load_config

from vts.llm import AgentConfigError, chat_with_agent

def get_reply(user_text: str) -> str:
    "Get the agent reply for the given user text."
    # process user text and get output/reply text
    reply = create_guest_bot(user_text)
    # try directly in memoryless mode because the indirect step failed
    if not reply:
        config = load_config()
        # a direct connection is possible
        if 'agent' in config:
            print(user_text)
            reply = chat_with_agent(user_text, [], stateless=True)[0]
            print(reply)
        # provide contact information
        else:
            reply = "I'm sorry, but the connection to the agent is unavailable. " \
                "You can email the CSEE department at **dept@cs.umbc.edu** " \
                "or call **410-455-3500**.\n"
    return reply

def reply_to_message():
    "This function gets text and makes a reply using get_echo_output"
    user_text = request.json.get("message", "")
    # Note: These error strings probably should be logged or printed
    # instead of being exposed in the chat reply to the end user like
    # this. However, if only developers, testers, and graders are
    # using this right now, then it helps to get exact feedback
    # immediately. Change the error handling to log the error message
    # and send the generic contact information error if you deploy the
    # application.
    try:
        reply = get_reply(user_text)
    except ConfigPathError as e:
        reply = f"Error in configuration path: The file {e.args[0]} does not exist."
    except AgentConfigError as e:
        reply = f"Error in configuration file: The required agent field '{e.args[0]}' is missing."
    md = MarkdownIt('commonmark', {'breaks':False, 'html':True}).enable('table')
    json_reply = jsonify({"reply": md.render(reply),
                          "unformatted_reply": reply})
    return json_reply
