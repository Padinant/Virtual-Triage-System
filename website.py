"""
Web server layer that serves HTML, CSS, JSON, etc.
"""

import os
import secrets

import markdown

from flask import Flask
from flask import Response
from flask import render_template
from flask import request, jsonify

from database import create_debug_database
from database import fill_debug_database
from database import get_debug_database
from database import users_to_json

import string

app = Flask(__name__)
app.secret_key = secrets.token_hex()

def init_db ():
    "Initializes the debug/testing database."
    print("Debug/testing DB not found! Creating it.")
    db = create_debug_database(False)
    print("Populating the database.")
    fill_debug_database(db)
    return db

def setup_app():
    "Makes sure that the app has everything that it needs on startup."
    # If the instance path that Flask uses for data doesn't exist,
    # create it now.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    # The database must be in the instance directory.
    db_path = os.path.join(app.instance_path, 'test.db')
    print(db_path)
    # If the database is not there, then create it and populate it.
    if not os.path.exists(db_path):
        init_db()

setup_app()

# A temporary Markdown string to test placing Markdown in the HTML.
# Note that Markdown generates HTML so the template must mark the
# variable as |safe in order for the HTML to not be escaped.
LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit," \
      "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua." \
      "Ut enim ad minim veniam, **quis** nostrud exercitation ullamco laboris" \
      "nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor" \
      "in reprehenderit in voluptate velit esse cillum dolore eu fugiat" \
      "nulla pariatur. Excepteur sint occaecat cupidatat non proident," \
      "sunt in culpa qui officia deserunt mollit anim **id est** laborum."

@app.route("/")
def home():
    "The main entry point to the app."
    return render_template('index.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/index.html")
def index():
    "Another name for the main entry point."
    return render_template('index.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/style.css")
def stylesheet():
    "The CSS file shared by all webpages."
    return render_template('style.css')


### CHATBOT PAGE SPECIFICS

@app.route("/chat.html")
def chat():
    "The chatbot page."
    return render_template('chat.html', page_body_text = markdown.markdown(LOREM_IPSUM))

def get_echo_output(user_text: string) -> string:
    "This is the first output function for sprint 1. Returns an excited echo"
    if not user_text:
        return "Say Something!" # this is just contingency, it shouldn't be displayed
    else:
        return user_text + "!"

# API endpoint for chat messages (in future versions this is where we'd get chatbot output)
@app.route("/message", methods=["POST"])
def message():
    "This function gets text and makes a reply using get_echo_output"
    # get user text
    user_text = request.json.get("text", "")
    # process user text and get output/reply text
    reply = get_echo_output(user_text)
    return jsonify({"reply": reply})

###

@app.route("/faq_list.html")
def faq_list():
    "The list of FAQ items."
    return render_template('index.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/faq_search.html")
def faq_search():
    "The FAQ search page."
    return render_template('index.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/faq_admin.html")
def faq_admin():
    "The admin FAQ list page."
    return render_template('index.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/faq_admin_search.html")
def faq_admin_search():
    "The admin FAQ search page."
    return render_template('index.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/faq_admin_add.html")
def faq_admin_add():
    "The admin FAQ page for adding items."
    return render_template('index.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/faq_admin_edit.html")
def faq_admin_edit():
    "The admin FAQ page for editing items."
    return render_template('index.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/faq_admin_remove.html")
def faq_admin_remove():
    "The admin FAQ page for removing items."
    return render_template('index.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/api.json")
def json_api_hello_world():
    "A temporary JSON file to demonstrate how APIs could work."
    db = get_debug_database(False)
    return Response(response=users_to_json(db),
                    mimetype='application/json')
