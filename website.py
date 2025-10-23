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
from database import Engine
from database import get_debug_database
from database import get_faq_entries
from database import users_to_json

from test_data import fill_debug_database

import string

app = Flask(__name__)
app.secret_key = secrets.token_hex()

def init_db ():
    "Initializes the debug/testing database."
    print("Debug/testing DB not found! Creating it.")
    db = create_debug_database(Engine.SQLITE_FILE)
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

def faq_entries_to_markdown(faq_entries):
    return [markdown.markdown(item[0]) + '\n\n' + markdown.markdown(item[1]) + '\n\n'
            for item in faq_entries]

def faq_titles_to_markdown(faq_entries):
    return [markdown.markdown(item[0]) + '\n\n'
            for item in faq_entries]

def get_faq_entries_as_markdown(database):
    entries = get_faq_entries(database)
    return faq_entries_to_markdown(entries)

def get_faq_titles_as_markdown(database):
    entries = get_faq_entries(database)
    return faq_titles_to_markdown(entries)

MENU_ITEMS = [{'name': 'FAQs',
               'url': '#'},
              {'name': 'Search Questions',
               'url': '#'},
              {'name': 'Use Chatbot',
               'url': '#'},
              {'name': 'Contact Us',
               'url': '#'},
              {'name': 'Department Website',
               'url': '#'},
              {'name': 'How to Use This Tool',
               'url': '#'}]

@app.route("/")
def home():
    "The main entry point to the app."
    items = get_faq_titles_as_markdown(get_debug_database(False))
    return render_template('MainPage.html',
                           menu_items = MENU_ITEMS,
                           faq_items = items)

@app.route("/index.html")
def index():
    "Another name for the main entry point."
    items = get_faq_titles_as_markdown(get_debug_database(False))
    return render_template('MainPage.html',
                           menu_items = MENU_ITEMS,
                           faq_items = items)

@app.route("/faq-page.html")
def faq_page():
    "The list of FAQ items."
    items = get_faq_entries_as_markdown(get_debug_database(False))
    return render_template('FAQPage.html',
                           menu_items = MENU_ITEMS,
                           faq_items = items)

@app.route("/style.css")
def stylesheet():
    "The CSS file shared by all webpages."
    return render_template('style.css')

@app.route("/MainPage.css")
def main_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('MainPage.css'),
                    mimetype='text/css')

@app.route("/FAQPage.css")
def faq_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('FAQPage.css'),
                    mimetype='text/css')

@app.route("/AdminAdd.css")
def admin_add_css():
    "The CSS file shared by all webpages."
    return render_template('AdminAdd.css')

@app.route("/AdminEdit.css")
def admin_edit_css():
    "The CSS file shared by all webpages."
    return render_template('AdminEdit.css')

@app.route("/AdminRemove.css")
def admin_remove_css():
    "The CSS file shared by all webpages."
    return render_template('AdminRemove.css')

@app.route("/AdminFAQ.css")
def admin_faq_css():
    "The CSS file shared by all webpages."
    return render_template('AdminFAQ.css')

@app.route("/AdminSearchResults.css")
def admin_search_results_css():
    "The CSS file shared by all webpages."
    return render_template('AdminSearchResults.css')

### CHATBOT PAGE SPECIFICS

@app.route("/chat.html")
def chat():
    "The chatbot page."
    return render_template('chat.html')

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

@app.route("/faq_search.html")
def faq_search():
    "The FAQ search page."
    return render_template('SearchResultsPage.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/faq_admin.html")
def faq_admin():
    "The admin FAQ list page."
    return render_template('AdminFAQ.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/faq_admin_search.html")
def faq_admin_search():
    "The admin FAQ search page."
    return render_template('AdminSearchResults.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/faq_admin_add.html")
def faq_admin_add():
    "The admin FAQ page for adding items."
    return render_template('AdminAdd.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/faq_admin_edit.html")
def faq_admin_edit():
    "The admin FAQ page for editing items."
    return render_template('AdminEdit.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/faq_admin_remove.html")
def faq_admin_remove():
    "The admin FAQ page for removing items."
    return render_template('AdminRemove.html', page_body_text = markdown.markdown(LOREM_IPSUM))

@app.route("/api.json")
def json_api_hello_world():
    "A temporary JSON file to demonstrate how APIs could work."
    db = get_debug_database(False)
    return Response(response=users_to_json(db),
                    mimetype='application/json')
