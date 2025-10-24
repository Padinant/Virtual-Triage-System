import string

from flask import request, jsonify

def get_echo_output(user_text: string) -> string:
    "This is the first output function for sprint 1. Returns an excited echo"
    if not user_text:
        return "Say Something!" # this is just contingency, it shouldn't be displayed
    else:
        return user_text + "!"

def reply_to_message():
    "This function gets text and makes a reply using get_echo_output"
    # get user text
    user_text = request.json.get("text", "")
    # process user text and get output/reply text
    reply = get_echo_output(user_text)
    return jsonify({"reply": reply})
