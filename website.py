"""
Web server layer that serves HTML, CSS, JSON, etc.
"""

import os
import secrets

import markdown

from flask import Flask
from flask import Response
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for

from chat import reply_to_message
from database import AppDatabase
from database import Engine
from frontend import ADMIN_ITEMS
from frontend import MENU_ITEMS

from test_data import fill_debug_database

app = Flask(__name__)
app.secret_key = secrets.token_hex()

def init_db ():
    "Initializes the debug/testing database."
    print("Debug/testing DB not found! Creating it.")
    db = AppDatabase(Engine.SQLITE_FILE)
    db.initialize_metadata()
    print("Populating the database.")
    fill_debug_database(db)

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

# This provides a section separator (which should be HTML <hr />) to
# the end of certain markdown items.
MARKDOWN_SEPARATOR = markdown.markdown('---')

def faq_entries_to_markdown(faq_entries):
    "Turn FAQ questions and answers into markdown."
    return [{'text': markdown.markdown(item['question_text']) +
             markdown.markdown(item['answer_text']) +
             MARKDOWN_SEPARATOR,
             'id': item['id']}
            for item in faq_entries]

def faq_titles_to_markdown(faq_entries):
    "Turn FAQ questions into markdown."
    return [{'text': markdown.markdown(item['question_text']),
             'url': f'/faq/{item['id']}'}
            for item in faq_entries]

def get_faq_entries_as_markdown(db):
    "Retrieve all FAQ entries as markdown."
    return faq_entries_to_markdown(db.faq_entries())

def get_faq_entry_as_markdown(faq_id):
    "Retrieve all FAQ entries as markdown."
    return lambda db : faq_entries_to_markdown(db.faq_entry(faq_id))

def get_faq_titles_as_markdown(db):
    "Retrieve all FAQ titles (questions) as markdown."
    return faq_titles_to_markdown(db.faq_entries())

def page_from_faq_action(page, action, db):
    "Generate a page by calling an action function on the database."
    items = action(db)
    categories = db.faq_categories()
    return render_template(page,
                           menu_items = MENU_ITEMS,
                           category_items = categories,
                           faq_items = items)

def main_page_from_faq_action(page, action, db):
    "Generate a page by calling an action function on the database with admin links."
    items = action(db)
    return render_template(page,
                           menu_items = MENU_ITEMS,
                           faq_items = items,
                           admin_items = ADMIN_ITEMS)

@app.route("/")
def home():
    "The main entry point to the app."
    db = AppDatabase(Engine.SQLITE_FILE)
    return main_page_from_faq_action('main-page.html',
                                     get_faq_titles_as_markdown,
                                     db)

@app.route("/index.html")
def index():
    "Another name for the main entry point."
    db = AppDatabase(Engine.SQLITE_FILE)
    return main_page_from_faq_action('main-page.html',
                                     get_faq_titles_as_markdown,
                                     db)

@app.route("/faq/")
def faq_page():
    "The list of FAQ items."
    db = AppDatabase(Engine.SQLITE_FILE)
    return page_from_faq_action('faq-page.html',
                                get_faq_entries_as_markdown,
                                db)

@app.route("/faq/<int:faq_id>")
def faq_item_page(faq_id):
    "The page for a specific FAQ item."
    db = AppDatabase(Engine.SQLITE_FILE)
    return page_from_faq_action('faq-page.html',
                                get_faq_entry_as_markdown(faq_id),
                                db)

@app.route("/search")
def faq_search_page():
    "The FAQ search landing page."
    return render_template('search.html',
                           menu_items = MENU_ITEMS)

@app.route("/search.html")
def faq_search():
    "The FAQ search page."
    db = AppDatabase(Engine.SQLITE_FILE)
    return page_from_faq_action('search.html',
                                get_faq_entries_as_markdown,
                                db)

@app.route("/admin-faq.html")
def faq_admin():
    "The admin FAQ list page."
    db = AppDatabase(Engine.SQLITE_FILE)
    return page_from_faq_action('admin-faq.html',
                                get_faq_entries_as_markdown,
                                db)

@app.route("/admin-search.html")
def faq_admin_search():
    "The admin FAQ search page."
    db = AppDatabase(Engine.SQLITE_FILE)
    return page_from_faq_action('admin-search.html',
                                get_faq_entries_as_markdown,
                                db)

@app.route("/add/")
def faq_admin_add():
    "The admin FAQ page for adding items."
    return render_template('admin-add.html',
                           menu_items = MENU_ITEMS)

@app.route("/edit/<int:faq_id>")
def faq_admin_edit(faq_id):
    "The admin FAQ page for editing an individual item."
    db = AppDatabase(Engine.SQLITE_FILE)
    faq_entry = db.faq_entry(faq_id)[0]
    return render_template('admin-edit.html',
                           menu_items = MENU_ITEMS,
                           faq_entry = faq_entry)

@app.route('/edit/')
def edit_root():
    "The root edit directory redirects because it only makes sense if an ID is provided."
    return redirect(url_for('faq_admin'))

@app.route("/remove/<int:faq_id>")
def faq_admin_remove(faq_id):
    "The admin FAQ page for removing an individual item."
    db = AppDatabase(Engine.SQLITE_FILE)
    return page_from_faq_action('admin-remove.html',
                                get_faq_entry_as_markdown(faq_id),
                                db)

@app.route('/remove/')
def remove_root():
    "The root remove directory redirects because it only makes sense if an ID is provided."
    return redirect(url_for('faq_admin'))

# Input

@app.route("/add/", methods=["POST"])
def faq_admin_add_post():
    "Adds a new post to the database."
    print(request.form['question'])
    print(request.form['answer'])
    print(request.form['category'])
    return "Success!"

@app.route("/edit/<int:faq_id>", methods=["POST"])
def faq_admin_edit_post(faq_id):
    "Updates the given ID's post to contain the new data."
    print(faq_id)
    print(request.form['question'])
    print(request.form['answer'])
    print(request.form['category'])
    return "Success!"

@app.route("/remove/<int:faq_id>", methods=["POST"])
def faq_admin_remove_post(faq_id):
    "Removes the given post ID."
    print(faq_id)
    print(request.form['confirm'] and request.form['confirm'] == 'yes')
    return "Success!"

# Style pages

@app.route("/base.css")
def base_css():
    "The base CSS file with variables and global styles."
    return Response(response=render_template('base.css'),
                    mimetype='text/css')

@app.route("/style.css")
def stylesheet():
    "The CSS file shared by all webpages."
    return send_from_directory(app.static_folder, 'style.css', mimetype='text/css')

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

@app.route("/search.css")
def search_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('search.css'),
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

@app.route("/admin-search.css")
def admin_search_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('admin-search.css'),
                    mimetype='text/css')

@app.route("/chat.css")
def chat_css():
    "The CSS file for the chat page."
    return Response(response=render_template('chat.css'),
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
    db = AppDatabase(Engine.SQLITE_FILE)
    return db.users_to_jsonable()
