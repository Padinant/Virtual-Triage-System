"""
Test the parts of website.py that are best tested through code instead
of through stepping through every web page. This may change in the
final sprint.
"""

from pytest import fixture

from werkzeug.test import Client

# from flask_bcrypt import Bcrypt

from test_database import mock_categories, mock_database_users, mock_faq_entries

from vts.database import Engine
from vts.frontend import MENU_ITEMS
from vts.frontend import TITLES
from vts.test_data import TEST_FAQ
from vts.website import TEST_ENGINE
from vts.website import app
from vts.website import create_home
from vts.website import faq_entries_to_markdown
from vts.website import faq_titles_to_markdown
from vts.website import flask_bcrypt
from vts.website import init_db
from vts.website import markdown

TEST_ENGINE = Engine.SQLITE_MEMORY

# Unit tests

def test_faq_entries_to_markdown():
    "Do the FAQ entries correctly convert to the expected data structure?"
    # First, we build the expected list of dicts.
    html_string = [markdown(question) + markdown('---') + markdown(answer)
                   for question, answer, category in TEST_FAQ]
    expected_items = []
    for i, text in enumerate(html_string):
        expected_items.append({'text': text,
                               'question_text': TEST_FAQ[i][0],
                               'answer_text' : TEST_FAQ[i][1],
                               'id': i + 1})

    # Next, we build the input list of dicts.
    faq_entries = []
    for i, entry in enumerate(TEST_FAQ):
        question, answer, category = entry
        faq_entries.append({'question_text': question,
                            'answer_text': answer,
                            'id': i + 1})

    # Finally, we check to see if the function output matches.
    assert faq_entries_to_markdown(faq_entries) == expected_items

def test_faq_titles_to_markdown():
    "Do the FAQ titles correctly convert to the expected data structure?"
    # First, we build the expected list of dicts.
    html_string = [markdown(question) for question, answer, category in TEST_FAQ]
    expected_items = []
    for i, text in enumerate(html_string):
        expected_items.append({'text': text, 'url': f'/faq/{i + 1}'})

    # Next, we build the input list of dicts.
    faq_entries = []
    for i, entry in enumerate(TEST_FAQ):
        question, answer, category = entry
        faq_entries.append({'question_text': question,
                            'answer_text': answer,
                            'id': i + 1})

    # Finally, we check to see if the function output matches.
    assert faq_titles_to_markdown(faq_entries) == expected_items

# Integration Tests Part 1: Server Only
#
# Note: pylint can't handle pytest's fixtures so redefined-outer-name
# has to be disabled here.

# These are the pages restricted by admin access. The ones with false
# in the second tuple field are ones that are dangerous to run
# directly because they immediately have side effects.
ADMIN_PAGES = [("/admin-categories.html", True),
               ("/admin-categories/add", True),
               ("/admin-categories/edit/1", True),
               ("/admin-categories/remove/1", True),
               ("/add/", True),
               ("/edit/1", True),
               ("/remove/1", True),
               ("/admin-logout.html", False),
               ("/admin-reset-test-db", False)]

@fixture()
def flask_app():
    "Tests the Flask flask_app."
    yield app

@fixture()
# pylint:disable-next=redefined-outer-name
def client(flask_app):
    "Creates a test server for Flask."
    c = Client(flask_app)
    yield c

@fixture()
# pylint:disable-next=redefined-outer-name,unused-argument
def sqlite_db(flask_app, client):
    "Creates a test database for Flask."
    db = init_db(TEST_ENGINE, flask_bcrypt)
    yield db

# pylint:disable-next=redefined-outer-name
def test_404_page(client):
    "Does the 404 page function correctly?"
    response = client.get('/404')
    assert response.status_code == 404

# pylint:disable-next=redefined-outer-name
def test_admin_login_wall(client):
    "Without logging in, do all of the admin pages return 403?"
    for page in ADMIN_PAGES:
        print("Trying to access page " + page[0])
        response = client.get(page[0])
        assert response.status_code == 403

# Integration Tests Part 2: Server and Database

# pylint:disable-next=redefined-outer-name
def test_home(sqlite_db):
    "Does the data sent to the template for the home page match expectations?"
    faq_categories, faq_category_names, faq_category_index = mock_categories()
    users = mock_database_users()
    faq_entries = mock_faq_entries(faq_categories, faq_category_names, faq_category_index, users)
    home = create_home(sqlite_db, None)
    expected = {'title': TITLES['main-page'],
                'menu_items': MENU_ITEMS,
                'faq_items': faq_titles_to_markdown(faq_entries),
                'faq_full_items': faq_entries_to_markdown(faq_entries),
                'admin': None}
    # Timestamps aren't going to match so we didn't even mock them.
    # Let's pop them.
    for entry in home['faq_full_items']:
        entry.pop('timestamp', None)
    assert home == expected
