"""
Web server layer that serves HTML, CSS, JSON, etc.
"""

import secrets

import markdown

from flask import Flask
from flask import render_template
from flask import session

from database import create_debug_database
from database import fill_debug_database
from database import print_all_users

app = Flask(__name__)
app.secret_key = secrets.token_hex()

def init_db ():
    db = create_debug_database(False)
    fill_debug_database(db)
    return db

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

@app.route("/chat.html")
def chat():
    "The chatbot page."
    return render_template('index.html', page_body_text = markdown.markdown(LOREM_IPSUM))

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

# TODO: provide a JSON file of all of the users from the database
@app.route("/api.json")
def json_api_hello_world():
    "A temporary JSON file to demonstrate how APIs could work."
    db = init_db()
    print_all_users(db)
    return {}
