"""
Web server layer that serves HTML, CSS, JSON, etc.
"""

import os

import secrets

from typing import Optional

from datetime import datetime

from markdown_it import MarkdownIt

from flask import Flask
from flask import Response
from flask import abort
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from flask_bcrypt import Bcrypt

from vts.chat import reply_to_message

from vts.config import load_postgres_config

from vts.database import AppDatabase
from vts.database import Engine
from vts.database import FAQEntry
from vts.database import FAQCategory

from vts.frontend import MENU_ITEMS

from vts.test_data import fill_debug_database

from vts.search import ensure_index
from vts.search import build_index
from vts.search import search_faq_ids
from vts.search import fetch_entries_by_ids
from vts.search import add_faq_to_index
from vts.search import update_faq_in_index
from vts.search import remove_faq_from_index

app = Flask(__name__)
flask_bcrypt = Bcrypt(app)

def get_db () -> AppDatabase:
    "Retrieves the appropriate database."
    postgres = load_postgres_config()
    if postgres:
        return AppDatabase(Engine.POSTGRESQL,
                           username = postgres["username"],
                           password = postgres["password"],
                           host = postgres["host"] if "host" in postgres else False)
    return AppDatabase(Engine.SQLITE_FILE)

def init_db ():
    "Initializes the debug/testing database."
    print("Debug/testing DB not found! Creating it.")
    db = AppDatabase(Engine.SQLITE_FILE)
    db.initialize_metadata()
    print("Populating the database.")
    fill_debug_database(db, flask_bcrypt)

def setup_app():
    "Makes sure that the app has everything that it needs on startup."
    # If the instance path that Flask uses for data doesn't exist,
    # create it now.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    # Create the secret key for the cookies
    secret_path = os.path.join(app.instance_path, '.secret')
    if not os.path.exists(secret_path):
        secrets.token_hex()
        with open(secret_path, mode='w', encoding='utf8') as secret_file:
            secret_file.write(secrets.token_hex())
    with open(secret_path, mode='r', encoding='utf8') as secret_file:
        app.secret_key = secret_file.read()
    # The database must be in the instance directory.
    db_path = os.path.join(app.instance_path, 'test.db')
    # The path must be cached for future AppDatabase instances.
    AppDatabase.path = db_path
    # If the database is not there, then create it and populate it.
    fresh_db = False
    if not os.path.exists(db_path):
        init_db()
        fresh_db = True
    # Builds search index.
    db = get_db()
    if fresh_db:
        build_index(db, app.instance_path)
    else:
        ensure_index(db, app.instance_path)

setup_app()

def delete_test_db():
    "Delete the test DB so the DB can be recreated."
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    db_path = os.path.join(app.instance_path, 'test.db')
    print('Removing test database at ' + db_path)
    os.remove(db_path)
    return True

def markdown(text: str):
    "Gives a modern table-friendly markdown renderer an API similar to the legacy one."
    md = MarkdownIt('commonmark', {'breaks':True, 'html':True}).enable('table')
    return md.render(text)

# This provides a section separator (which should be HTML <hr />) to
# the end of certain markdown items.
MARKDOWN_SEPARATOR = markdown('---')

def faq_entries_to_markdown(faq_entries: list[dict]) -> list[dict]:
    "Turn FAQ questions and answers into markdown."
    result = []
    for item in faq_entries:
        entry = item.copy()
        question = markdown(item['question_text'])
        answer = markdown(item['answer_text'])
        markdown_text = question + MARKDOWN_SEPARATOR + answer
        entry['text'] = markdown_text
        result.append(entry)
    return result

def faq_titles_to_markdown(faq_entries: list[dict]) -> list[dict]:
    "Turn FAQ questions into markdown."
    return [{'text': markdown(item['question_text']),
             'url': f'/faq/{item["id"]}'}
            for item in faq_entries]

def get_faq_entries_as_markdown(db: AppDatabase):
    "Retrieve all FAQ entries as markdown."
    return faq_entries_to_markdown(db.faq_entries())

def get_faq_categorized_entries_as_markdown(db: AppDatabase, category_id: int):
    "Retrieve FAQ entries as markdown in a category."
    return faq_entries_to_markdown(db.faq_entries_by_category(category_id))

def get_faq_entry_as_markdown(faq_id: int):
    "Retrieve all FAQ entries as markdown."
    return lambda db : faq_entries_to_markdown(db.faq_entry(faq_id))

def get_faq_titles_as_markdown(db: AppDatabase):
    "Retrieve all FAQ titles (questions) as markdown."
    return faq_titles_to_markdown(db.faq_entries())

# This is based on the assumption that there aren't many categories
# and that it's cheaper to iterate over the category dict than to talk
# to the database again.
def find_category_name(categories: list[dict], category_id: int) -> str:
    "Return the name for a category id."
    for category in categories:
        if category['id'] == category_id:
            return category['category_name']
    return ''

def get_admin_status() -> Optional[dict]:
    "Returns true if the user is logged in, i.e. if the user's session has a username."
    if 'username' in session and 'user_id' in session:
        return {'username': session['username'],
                'user_id': session['user_id']}
    return None

@app.route("/")
def home():
    "The main entry point to the app."
    db = get_db()
    items = get_faq_titles_as_markdown(db)
    full_items = get_faq_entries_as_markdown(db)
    return render_template('main-page.html',
                           title="Interactive Help" \
                           " - UMBC Computer Science & Electrical Engineering",
                           menu_items=MENU_ITEMS,
                           faq_items=items,
                           faq_full_items=full_items,
                           admin_items=[],
                           admin=get_admin_status())

@app.route("/how-to.html")
def how_to_page():
    "The how-to guide page."
    return render_template('how-to.html',
                           title="How to Use This Tool - Interactive Help",
                           menu_items=MENU_ITEMS,
                           admin=get_admin_status())

# Note: This no longer has a route of its own. You get here from the
# FAQ search page if you are logged in.
def faq_admin():
    "The admin FAQ with search page."
    db = get_db()
    query = request.args.get('query', '').strip()
    category = request.args.get('category', '').strip()
    if category:
        try:
            category_id = int(category)
        except ValueError:
            category_id = None
        if category_id is not None:
            items = get_faq_categorized_entries_as_markdown(db, category_id)
        else:
            items = get_faq_entries_as_markdown(db)
    elif query:
        matched_ids = search_faq_ids(query, app.instance_path)
        faq_entries = fetch_entries_by_ids(db, matched_ids) if matched_ids else []
        items = faq_entries_to_markdown(faq_entries)
    else:
        items = get_faq_entries_as_markdown(db)
    categories = db.faq_categories()
    selected_category = 'All Categories'
    if category and category_id is not None:
        name = find_category_name(categories, category_id)
        if name:
            selected_category = name

    return render_template('admin-faq-search.html',
                           title="Admin FAQ Management - Interactive Help",
                           menu_items=MENU_ITEMS,
                           category_items=categories,
                           faq_items=items,
                           query=query,
                           selected_category=selected_category,
                           test_db=db.engine_type == Engine.SQLITE_FILE,
                           admin=get_admin_status())

@app.route("/faq-search.html")
def faq_page():
    "The FAQ with search page."
    if get_admin_status():
        return faq_admin()
    db = get_db()
    query = request.args.get('query', '').strip()
    if query:
        matched_ids = search_faq_ids(query, app.instance_path)
        faq_entries = fetch_entries_by_ids(db, matched_ids) if matched_ids else []
        items = faq_entries_to_markdown(faq_entries)
    else:
        items = get_faq_entries_as_markdown(db)
    categories = db.faq_categories()
    # Default selected category for the public FAQ page is 'All Categories'
    selected_category = 'All Categories'
    return render_template('faq-search.html',
                           title="Browse FAQ - Interactive Help",
                           menu_items=MENU_ITEMS,
                           category_items=categories,
                           faq_items=items,
                           query=query,
                           selected_category=selected_category,
                           admin=None)

@app.route("/faq/<int:faq_id>")
def faq_item_page(faq_id: int):
    "The page for a specific FAQ item."
    db = get_db()
    items = get_faq_entry_as_markdown(faq_id)(db)
    categories = db.faq_categories()
    admin_status = get_admin_status()
    template_page = 'admin-faq-search.html' if admin_status else 'faq-search.html'
    selected_category = 'All Categories'
    if items:
        category_id = items[0].get('category_id')
        if category_id is not None:
            name = find_category_name(categories, category_id)
            if name:
                selected_category = name
    return render_template(template_page,
                           title=f"FAQ Item #{faq_id} - Interactive Help",
                           menu_items=MENU_ITEMS,
                           category_items=categories,
                           faq_items=items,
                           selected_category=selected_category,
                           admin=admin_status)

@app.route("/faq/category/<int:category_id>")
def faq_category_page(category_id: int):
    "The page for all entries of a given category."
    db = get_db()
    items = get_faq_categorized_entries_as_markdown(db, category_id)
    categories = db.faq_categories()
    name = find_category_name(categories, category_id)
    template_page = 'admin-faq-search.html' if get_admin_status() else 'faq-search.html'
    # When viewing a specific category, set the selected category name
    return render_template(template_page,
                           title=f"FAQ Category #{category_id} - {name} - Interactive Help",
                           menu_items=MENU_ITEMS,
                           category_items=categories,
                           faq_items=items,
                           selected_category=name,
                           admin=get_admin_status())

@app.route("/admin-login.html")
def admin_login():
    "The admin login page."
    # If already logged in, don't login again.
    if get_admin_status():
        return redirect(url_for('faq_page'))

    return render_template('admin-login.html',
                           title="Admin Login - Interactive Help",
                           menu_items=MENU_ITEMS,
                           admin=None)

@app.route("/admin-categories.html")
def category_admin():
    "The admin page that lists and manages categories."
    if not get_admin_status():
        abort(403)

    db = get_db()
    categories = db.faq_categories()
    for cat in categories:
        cat['is_empty'] = db.is_empty_category(cat['id'])
    return render_template('admin-category-list.html',
                           title="Admin Category Management - Interactive Help",
                           menu_items=MENU_ITEMS,
                           category_items=categories,
                           admin=get_admin_status())

@app.route("/admin-categories/add")
def category_add():
    "Render the add-category form."
    if not get_admin_status():
        abort(403)

    return render_template('admin-category-add.html',
                           title="Add New Category - Admin",
                           menu_items=MENU_ITEMS,
                           form_data=None,
                           admin=get_admin_status())

@app.route("/admin-reset-test-db")
def admin_reset_test_db():
    "Reset the test database."
    if not get_admin_status():
        abort(403)

    db_type = get_db().engine_type
    if db_type != Engine.SQLITE_FILE:
        flash('Error: Cannot remove the database because it is not a test database!')
    else:
        delete_test_db()
        setup_app()
        flash('Successfully reset the test database!')
    return redirect(url_for('faq_page'))

@app.route("/admin-categories/add", methods=["POST"])
def category_add_post():
    "Create a new category from the form."
    if not get_admin_status():
        abort(403)

    db = get_db()
    category_name = request.form['category_name'].strip()
    priority = request.form['priority']

    form_data = {
        'category_name': request.form['category_name'],
        'priority': request.form['priority']
    }

    errors = []
    if not category_name:
        errors.append('Category name cannot be empty.')
    if db.category_name_exists(category_name):
        errors.append(
            f'A category named "{category_name}" already exists. '
            'Please choose a different name.'
        )

    if errors:
        for error in errors:
            flash(f'Error: {error}')
        return render_template('admin-category-add.html',
                               title="Add New Category - Admin",
                               menu_items=MENU_ITEMS,
                               form_data=form_data,
                               admin=get_admin_status())

    new_cat = FAQCategory(category_name=category_name,
                          priority=priority)
    db.add_item(new_cat)
    flash(f'Category "{category_name}" added successfully!')
    return redirect(url_for('category_admin'))

@app.route("/admin-categories/edit/<int:category_id>")
def category_edit(category_id: int):
    "Render edit form for a category."
    if not get_admin_status():
        abort(403)

    db = get_db()
    categories = db.faq_categories()
    category = next((c for c in categories if c['id'] == category_id), None)
    if not category:
        return redirect(url_for('category_admin'))
    return render_template('admin-category-edit.html',
                           title=f"Edit Category #{category_id} - Admin",
                           menu_items=MENU_ITEMS,
                           category=category,
                           admin=get_admin_status())

@app.route("/admin-categories/edit/<int:category_id>", methods=["POST"])
def category_edit_post(category_id: int):
    "Process category edits."
    if not get_admin_status():
        abort(403)

    db = get_db()
    new_name = request.form['category_name'].strip()
    priority = request.form['priority']

    form_data = {
        'id': category_id,
        'category_name': request.form['category_name'],
        'priority': request.form['priority']
    }

    categories = db.faq_categories()
    current_category = next((c for c in categories if c['id'] == category_id), None)
    if not current_category:
        return redirect(url_for('category_admin'))

    errors = []
    if not new_name:
        errors.append('Category name cannot be empty.')

    # Only check for duplicates if name changed
    elif current_category['category_name'].lower() != new_name.lower():
        if db.category_name_exists(new_name):
            errors.append(
                f'A category named "{new_name}" already exists. '
                'Please choose a different name.'
            )

    if errors:
        for error in errors:
            flash(f'Error: {error}')
        return render_template('admin-category-edit.html',
                               title=f"Edit Category #{category_id} - Admin",
                               menu_items=MENU_ITEMS,
                               category=form_data,
                               admin=get_admin_status())

    db.update_category(category_id, new_name, priority)
    flash(f'Category updated to "{new_name}" successfully!')
    return redirect(url_for('category_admin'))

@app.route("/admin-categories/remove/<int:category_id>")
def category_remove(category_id: int):
    "Show category remove confirmation."
    if not get_admin_status():
        abort(403)

    db = get_db()
    category = next((c for c in db.faq_categories() if c['id'] == category_id), None)
    if not category:
        return redirect(url_for('category_admin'))
    return render_template('admin-category-remove.html',
                           title=f"Remove Category #{category_id} - Admin",
                           menu_items=MENU_ITEMS,
                           category=category,
                           admin=get_admin_status())

@app.route("/admin-categories/remove/<int:category_id>", methods=["POST"])
def category_remove_post(category_id: int):
    "Perform category removal (marks as removed if not in use)."
    if not get_admin_status():
        abort(403)

    db = get_db()
    # Get category name before attempting removal
    categories = db.faq_categories()
    category = next((c for c in categories if c['id'] == category_id), None)
    category_name = category['category_name'] if category else f"#{category_id}"

    success = db.remove_category(category_id)
    if success:
        flash(f'Category "{category_name}" removed successfully!')
        return redirect(url_for('category_admin'))
    # Category in use - cannot remove
    flash(f'Error: Cannot remove category "{category_name}" because it is '
          f'currently in use by FAQ entries.')
    return redirect(url_for('category_admin'))

@app.route("/add/")
def faq_admin_add():
    "The admin FAQ page for adding items."
    if not get_admin_status():
        abort(403)

    db = get_db()
    categories = db.faq_categories()
    return render_template('admin-add.html',
                           title="Add New FAQ - Admin",
                           menu_items=MENU_ITEMS,
                           category_items=categories,
                           form_data=None,
                           admin=get_admin_status())

@app.route("/edit/<int:faq_id>")
def faq_admin_edit(faq_id: int):
    "The admin FAQ page for editing an individual item."
    if not get_admin_status():
        abort(403)

    db = get_db()
    faq_entry = db.faq_entry(faq_id)[0]
    categories = db.faq_categories()
    return render_template('admin-edit.html',
                           title=f"Edit FAQ #{faq_id} - Admin",
                           menu_items=MENU_ITEMS,
                           faq_entry=faq_entry,
                           category_items=categories,
                           admin=get_admin_status())

@app.route("/edit/")
def edit_root():
    "The root edit directory redirects because it only makes sense if an ID is provided."
    return redirect(url_for('faq_page'))

@app.route("/remove/<int:faq_id>")
def faq_admin_remove(faq_id):
    "The admin FAQ page for removing an individual item."
    if not get_admin_status():
        abort(403)

    db = get_db()
    faq_entries = db.faq_entry(faq_id)
    if not faq_entries:
        return redirect(url_for('faq_page'))
    items = get_faq_entry_as_markdown(faq_id)(db)
    categories = db.faq_categories()
    return render_template('admin-remove.html',
                           title=f"Remove FAQ #{faq_id} - Admin",
                           menu_items=MENU_ITEMS,
                           category_items=categories,
                           faq_items=items,
                           admin=get_admin_status())

@app.route("/remove/")
def remove_root():
    "The root remove directory redirects because it only makes sense if an ID is provided."
    return redirect(url_for('faq_page'))

# Input

@app.route("/admin-login.html", methods=["POST"])
def admin_login_post():
    "Handles admin login form submission."
    db = get_db()
    user_id = db.check_user_login(request.form['username'],
                                  request.form['password'],
                                  flask_bcrypt)

    if not user_id:
        flash('Login Error: Invalid Username and/or Password')
        return redirect(url_for('admin_login_post'))

    session['username'] = request.form['username']
    session['user_id'] = user_id

    return redirect(url_for('faq_page'))

@app.route("/admin-logout.html")
def admin_logout():
    "Logs the user out if the user navigates here."
    if not get_admin_status():
        abort(403)

    session.pop('username')
    session.pop('user_id')
    return redirect(url_for('home'))

@app.route("/add/", methods=["POST"])
def faq_admin_add_post():
    "Adds a new post to the database."
    if not get_admin_status():
        abort(403)

    db = get_db()
    question_text = request.form['question'].strip()
    answer_text = request.form['answer'].strip()
    category_id = request.form['category'].strip()
    priority = request.form['priority']

    form_data = {
        'question': request.form['question'],
        'answer': request.form['answer'],
        'category': request.form['category'],
        'priority': request.form['priority']
    }

    errors = []
    if not question_text:
        errors.append('Question field cannot be empty.')
    if not answer_text:
        errors.append('Answer field cannot be empty.')
    if not category_id:
        errors.append('Please select a category.')
    if not priority:
        errors.append('Please select a priority.')

    if errors:
        for error in errors:
            flash(f'Error: {error}')
        categories = db.faq_categories()
        return render_template('admin-add.html',
                               title="Add New FAQ - Admin",
                               menu_items=MENU_ITEMS,
                               category_items=categories,
                               form_data=form_data,
                               admin=get_admin_status())

    new_entry = FAQEntry(question_text = question_text,
                         answer_text = answer_text,
                         category_id = category_id,
                         author_id = session['user_id'],
                         priority = priority,
                         timestamp = datetime.now())

    faq_id = db.add_item(new_entry)

    # Incremental index update
    add_faq_to_index(db, faq_id, app.instance_path)
    flash(f'FAQ entry #{faq_id} added successfully!')

    return redirect(url_for('faq_item_page', faq_id = faq_id))

@app.route("/edit/<int:faq_id>", methods=["POST"])
def faq_admin_edit_post(faq_id: int):
    "Updates the given ID's post to contain the new data."
    if not get_admin_status():
        abort(403)

    db = get_db()
    question_text = request.form['question'].strip()
    answer_text = request.form['answer'].strip()
    category_id = request.form['category'].strip()
    priority = request.form['priority']

    form_data = {
        'id': faq_id,
        'question_text': request.form['question'],
        'answer_text': request.form['answer'],
        'category_id': request.form['category'],
        'priority': request.form['priority']
    }

    errors = []
    if not question_text:
        errors.append('Question field cannot be empty.')
    if not answer_text:
        errors.append('Answer field cannot be empty.')
    if not category_id:
        errors.append('Please select a category.')
    if not priority:
        errors.append('Please select a priority.')

    if errors:
        for error in errors:
            flash(f'Error: {error}')
        categories = db.faq_categories()
        return render_template('admin-edit.html',
                               title=f"Edit FAQ #{faq_id} - Admin",
                               menu_items=MENU_ITEMS,
                               faq_entry=form_data,
                               category_items=categories,
                               admin=get_admin_status())

    def query(statement):
        return statement.where(FAQEntry.id == faq_id)

    def update(item):
        item.question_text = question_text
        item.answer_text = answer_text
        item.category_id = category_id
        item.priority = priority
        item.author_id = session['user_id']
        item.timestamp = datetime.now()

    db.update_item(query, update)
    update_faq_in_index(db, faq_id, app.instance_path)
    flash(f'FAQ entry #{faq_id} updated successfully!')

    return redirect(url_for('faq_item_page', faq_id = faq_id))

@app.route("/remove/<int:faq_id>", methods=["POST"])
def faq_admin_remove_post(faq_id: int):
    "Removes the given post ID."
    if not get_admin_status():
        abort(403)

    db = get_db()

    if request.form['confirm'] and request.form['confirm'] == 'yes':
        db.remove_faq_entry(faq_id)
        remove_faq_from_index(faq_id, app.instance_path)
        flash(f'FAQ entry #{faq_id} removed successfully!')
    else:
        flash(f'FAQ entry #{faq_id} removal cancelled.')

    return redirect(url_for('faq_page'))

# HTML and Application Errors

@app.errorhandler(403)
def page_forbidden(error):
    "Handles the HTTP 403 error."
    title = 'HTTP 403 Error: Forbidden'
    return render_template('error.html',
                           title = title,
                           message = error,
                           admin=get_admin_status()), 403

@app.errorhandler(404)
def page_not_found(error):
    "Handles the HTTP 404 error."
    title = 'HTTP 404 Error: Page Not Found'
    return render_template('error.html',
                           title = title,
                           message = error,
                           admin=get_admin_status()), 404

# Style pages

@app.route("/base.css")
def base_css():
    "The base CSS file with variables and global styles."
    return Response(response=render_template('base.css'),
                    mimetype='text/css')

@app.route("/main-page.css")
def main_css():
    "The CSS file shared by all webpages."
    return Response(response=render_template('main-page.css'),
                    mimetype='text/css')

@app.route("/faq-search.css")
def faq_search_css():
    "The CSS file for the combined FAQ and search page."
    return Response(response=render_template('faq-search.css'),
                    mimetype='text/css')

@app.route("/how-to.css")
def how_to_css():
    "The CSS file for the how-to page."
    return Response(response=render_template('how-to.css'),
                    mimetype='text/css')

@app.route("/admin-login.css")
def admin_login_css():
    "The CSS file for the admin login page."
    return Response(response=render_template('admin-login.css'),
                    mimetype='text/css')

@app.route("/admin-faq-search.css")
def admin_faq_search_css():
    "The CSS file for the combined admin FAQ and search page."
    return Response(response=render_template('admin-faq-search.css'),
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

@app.route("/chat.css")
def chat_css():
    "The CSS file for the chat page."
    return Response(response=render_template('chat.css'),
                    mimetype='text/css')

@app.route("/chat.html")
def chat():
    "The chatbot page."
    return render_template(
        'chat.html',
        title="Ask Chatbot - Interactive Help",
        # Top menu
        menu_items=MENU_ITEMS,
        # Bottom menu
        bottom_menu_items=MENU_ITEMS,
        admin=get_admin_status())

# API endpoint for chat messages (in future versions this is where we'd get chatbot output)
@app.route("/message", methods=["POST"])
def message():
    "Calls the chatbot reply function, which returns a JSON result."
    return reply_to_message()

@app.route("/api.json")
def json_faq_api():
    "A JSON file that returns the FAQs as structured data for AI."
    db = get_db()
    return [{'question' : entry['question_text'],
             'answer'   : entry['answer_text']}
            for entry in db.faq_entries()]

@app.route("/api.txt")
def text_faq_api():
    "A TXT file that returns the FAQs all in one file for AI."
    db = get_db()
    faq_text = ''.join(['Question:\n' + entry['question_text'] + '\n\n'
                        + 'Answer:\n' + entry['answer_text'] + '\n---\n\n'
                        for entry in db.faq_entries()])
    return Response(response='---\n\n' + faq_text,
                    mimetype='text/plain')
