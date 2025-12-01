"""
Internal logic for the backend of the chatbot API.

This is a separate file to keep the website.py part of the chatbot
code as trivial as possible.
"""

from flask import request, jsonify

from vts.chat_server import create_guest_bot

def reply_to_message():
    "This function gets text and makes a reply using get_echo_output"
    # get user text
    user_text = request.json.get("message", "")
    # process user text and get output/reply text
    reply = create_guest_bot(user_text)
    return jsonify({"reply": reply})
