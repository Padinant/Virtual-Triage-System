"""
Web server layer that serves HTML, CSS, JSON, etc.
"""

import os
import secrets

import markdown

from flask import Flask
from flask import Response
from flask import render_template
from flask import jsonify

from chat import reply_to_message

from database import create_debug_database
from database import Engine
from database import get_debug_database
from database import get_faq_entries
from database import get_faq_entry
from database import users_to_jsonable

from test_data import fill_debug_database

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

def faq_entries_to_markdown(faq_entries):
    "Turn FAQ questions and answers into markdown."
    return [markdown.markdown(item[0]) + '\n\n' + markdown.markdown(item[1]) + '\n\n'
            for item in faq_entries]

def faq_titles_to_markdown(faq_entries):
    "Turn FAQ questions into markdown."
    return [markdown.markdown(item[0]) + '\n\n'
            for item in faq_entries]

def get_faq_entries_as_markdown(database):
    "Retrieve all FAQ entries as markdown."
    entries = get_faq_entries(database)
    return faq_entries_to_markdown(entries)

def get_faq_entry_as_markdown(faq_id):
    "Retrieve all FAQ entries as markdown."
    return lambda db : faq_entries_to_markdown(get_faq_entry(db, faq_id))

def get_faq_titles_as_markdown(database):
    "Retrieve all FAQ titles (questions) as markdown."
    entries = get_faq_entries(database)
    return faq_titles_to_markdown(entries)

MENU_ITEMS = [{'name': 'Browse the FAQs',
               'url': 'faq.html'},
              {'name': 'Search the FAQs',
               'url': 'search.html'},
              {'name': 'Use Chatbot',
               'url': 'chat.html'},
              {'name': 'Contact Us',
               'url': 'https://www.csee.umbc.edu/about_old/contact-us/'},
              {'name': 'Department Website',
               'url': 'https://www.csee.umbc.edu/'},
              {'name': 'How to Use This Tool',
               # This doesn't have a real URL yet!
               'url': '#'}]

ADMIN_ITEMS = [{'name': 'DEBUG Add Entry (ADMIN)',
                'url': 'admin-add.html'},
               {'name': 'DEBUG Edit Entry (ADMIN)',
                'url': 'admin-edit.html'},
               {'name': 'DEBUG Remove Entry (ADMIN)',
                'url': 'admin-remove.html'},
               {'name': 'DEBUG FAQ (ADMIN)',
                'url': 'admin-faq.html'},
               {'name': 'DEBUG Search (ADMIN)',
                'url': 'admin-search.html'}]

def page_from_faq_action(page, action, database):
    "Generate a page by calling an action function on the database."
    items = action(database)
    return render_template(page,
                           menu_items = MENU_ITEMS,
                           faq_items = items)

def main_page_from_faq_action(page, action, database):
    "Generate a page by calling an action function on the database with admin links."
    items = action(database)
    return render_template(page,
                           menu_items = MENU_ITEMS,
                           faq_items = items,
                           admin_items = ADMIN_ITEMS)

@app.route("/")
def home():
    "The main entry point to the app."
    return main_page_from_faq_action('main-page.html',
                                     get_faq_titles_as_markdown,
                                     get_debug_database(False))

@app.route("/index.html")
def index():
    "Another name for the main entry point."
    return main_page_from_faq_action('main-page.html',
                                     get_faq_titles_as_markdown,
                                     get_debug_database(False))

@app.route("/faq.html")
def faq_page():
    "The list of FAQ items."
    return page_from_faq_action('faq-page.html',
                                get_faq_entries_as_markdown,
                                get_debug_database(False))

@app.route("/faq/<int:faq_id>")
def faq_item_page(faq_id):
    "The page for a specific FAQ item."
    return page_from_faq_action('faq-page.html',
                                get_faq_entry_as_markdown(faq_id),
                                get_debug_database(False))

@app.route("/search.html")
def faq_search():
    "The FAQ search page."
    return page_from_faq_action('search-results.html',
                                get_faq_entries_as_markdown,
                                get_debug_database(False))

@app.route("/admin-faq.html")
def faq_admin():
    "The admin FAQ list page."
    return page_from_faq_action('admin-faq.html',
                                get_faq_entries_as_markdown,
                                get_debug_database(False))

@app.route("/admin-search.html")
def faq_admin_search():
    "The admin FAQ search page."
    return page_from_faq_action('admin-search.html',
                                get_faq_entries_as_markdown,
                                get_debug_database(False))

@app.route("/admin-add.html")
def faq_admin_add():
    "The admin FAQ page for adding items."
    return render_template('admin-add.html',
                           menu_items = MENU_ITEMS)

@app.route("/admin-edit.html")
def faq_admin_edit():
    "The admin FAQ page for editing items."
    return render_template('admin-edit.html',
                           menu_items = MENU_ITEMS)

@app.route("/admin-remove.html")
def faq_admin_remove():
    "The admin FAQ page for removing items."
    return render_template('admin-remove.html',
                           menu_items = MENU_ITEMS)

# Style pages

@app.route("/style.css")
def stylesheet():
    "The CSS file shared by all webpages."
    return render_template('style.css')

@app.route("/main-page.css")
def main_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('main-page.css'),
                    mimetype='text/css')

@app.route("/faq-page.css")
def faq_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('faq-page.css'),
                    mimetype='text/css')

@app.route("/faq/faq-page.css")
def faq_item_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('faq-page.css'),
                    mimetype='text/css')

@app.route("/search-results.css")
def search_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('search-results.css'),
                    mimetype='text/css')

@app.route("/admin-add.css")
def admin_add_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('admin-add.css'),
                    mimetype='text/css')

@app.route("/admin-edit.css")
def admin_edit_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('admin-edit.css'),
                    mimetype='text/css')

@app.route("/admin-remove.css")
def admin_remove_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('admin-remove.css'),
                    mimetype='text/css')

@app.route("/admin-faq.css")
def admin_faq_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('admin-faq.css'),
                    mimetype='text/css')

@app.route("/admin-search-results.css")
def admin_search_results_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('admin-search-results.css'),
                    mimetype='text/css')

@app.route("/chat.html")
def chat():
    "The chatbot page."
    return render_template('chat.html')

# API endpoint for chat messages (in future versions this is where we'd get chatbot output)
@app.route("/message", methods=["POST"])
def message():
    "Calls the chatbot reply function, which returns a JSON result."
    return reply_to_message()

@app.route("/api.json")
def json_api_hello_world():
    "A temporary JSON file to demonstrate how APIs could work."
    db = get_debug_database(False)
    return users_to_jsonable(db)
