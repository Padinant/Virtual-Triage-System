"""
Internal logic for the backend of the chatbot API.

This is a separate file to keep the website.py part of the chatbot
code as trivial as possible.
"""

from flask import request, jsonify

from markdown_it import MarkdownIt

from vts.chat_server import create_guest_bot

from vts.config import load_config

from vts.llm import chat_with_agent

def reply_to_message():
    "This function gets text and makes a reply using get_echo_output"
    # get user text
    user_text = request.json.get("message", "")
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
    # json_reply = jsonify({"reply": reply})
    md = MarkdownIt('commonmark', {'breaks':False, 'html':True}).enable('table')
    json_reply = jsonify({"reply": md.render(reply)})
    return json_reply
