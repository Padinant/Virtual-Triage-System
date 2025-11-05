"""
Test the database functionality.
"""

# Note that we have to import from both the database file and the file
# that contains the test data that we will fill a fresh database with.
from vts.database import AppDatabase
from vts.database import Engine
from vts.test_data import TEST_FAQ
from vts.test_data import TEST_FAQ_CATEGORIES
from vts.test_data import fill_debug_database

# Helper functions

def is_empty_list(obj):
    "Is the object an empty list?"
    return isinstance(obj, list) and not obj

def is_empty_dict(obj):
    "Is the object an empty dict?"
    return isinstance(obj, dict) and not obj

# Test functions

# Methods not yet directly tested: add_item(), add_items(),
# update_item(), remove_faq_entry(), faq_entries_by_category(), and
# delete_marked_entries()

def test_basic_database_functionality():
    "Test the basics of the database via exposed AppDatabase methods."
    # Initialize an empty SQLite database in memory. The subtle
    # differences between the SQLITE_MEMORY, SQLITE_FILE, and
    # POSTGRESQL should be handled by our libraries so we only need to
    # run these tests on the easiest of the three to test.
    db = AppDatabase(Engine.SQLITE_MEMORY)

    # Initialize the SQL table metadata. If we don't do this on the
    # first creation of an AppDatabase, then nothing else will work.
    db.initialize_metadata()

    # Assert that everything is empty in a fresh DB. Empty lists and
    # dicts are both false in Python so we need a slightly verbose
    # check of the type before checking for emptiness. We defined
    # functions earlier for this.
    assert is_empty_list(db.faq_entries())
    assert is_empty_list(db.faq_entries())
    assert is_empty_list(db.faq_categories())
    assert is_empty_dict(db.faq_categories_by_name())
    assert is_empty_list(db.faq_entries_by_category(0))
    assert is_empty_list(db.faq_entry(0))

    # Also assert that deleting marked entries in an empty database
    # deletes nothing. It normally returns a list of the deleted IDs,
    # so that list should be empty.
    assert is_empty_list(db.delete_marked_entries())

    # This inserts several users, categories, and FAQ entries, which
    # can then be verified based on our assumptions. This is done all
    # at once because the FAQEntries need Users and FAQCategories.
    fill_debug_database(db)

    # First, we assume that the categories are added in order and
    # become associated with an incrementing ID. Let's build the
    # same thing manually so we can compare.
    faq_categories = []
    faq_category_names = {}

    # We'll use enumerate() here due to the suggestion of Pylint. Note
    # that Python is 0-based and the SQL IDs are 1-based so an
    # addition has to be done.
    for i, category in enumerate(TEST_FAQ_CATEGORIES):
        category_id = i + 1
        faq_categories.append({'id': category_id, 'category_name': category})
        faq_category_names[category] = category_id

    # Does the database match our assumptions for FAQ categories?
    assert db.faq_categories() == faq_categories
    assert db.faq_categories_by_name() == faq_category_names

    # The two users as defined in fill_debug_database, except now
    # defined as a list of dicts here.
    users = [{'id': 1,
              'name': 'Guest',
             'campus_id': '',
             'email': '',
             'is_admin': False},
             {'id': 2,
              'name': 'Administrator',
             'campus_id': "FAKEID1",
             'email': "admin@example.com",
             'is_admin': True}]

    # Compare the returned user dicts to the expected user dict.
    assert db.users() == users

    # We'll do the same thing with the entries that we did with the
    # categories, creating a dict that should be what we get when we
    # query the database.
    faq_entries = []
    for i, entry in enumerate(TEST_FAQ):
        faq_question, faq_answer, faq_category = entry
        faq_id = i + 1
        faq_category_id = faq_category_names[faq_category]
        faq_entries.append({'id': faq_id,
                            'question_text': faq_question,
                            'answer_text': faq_answer,
                            'category_id': faq_category_id,
                            'author_id': 2})

    # Now we'll check our assumptions. Note the off-by-one again when
    # comparing SQL IDs to Python indexing.
    assert db.faq_entries() == faq_entries
    assert db.faq_entry(3) == [faq_entries[2]]
