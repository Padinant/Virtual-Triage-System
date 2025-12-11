"""
Test the database functionality.
"""

from datetime import datetime

from functools import reduce

# Note that we have to import from both the database file and the file
# that contains the test data that we will fill a fresh database with.
from vts.database import AppDatabase
from vts.database import Engine
from vts.database import FAQCategory
from vts.database import FAQEntry
from vts.database import User
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

def create_db_and_initialize():
    "Creates an initialized AppDatabase object."
    # Initialize an empty SQLite database in memory. The subtle
    # differences between the SQLITE_MEMORY, SQLITE_FILE, and
    # POSTGRESQL should be handled by our libraries so we only need to
    # run these tests on the easiest of the three to test.
    db = AppDatabase(Engine.SQLITE_MEMORY)

    # Initialize the SQL table metadata. If we don't do this on the
    # first creation of an AppDatabase, then nothing else will work.
    db.initialize_metadata()

    return db

# Test functions

# Note that the test scope isn't entirely comprehensive for Sprint 2.
#
# AppDatabase methods only indirectly tested at the moment:
# add_items()
#
# AppDatabase methods not yet tested: add_items(), update_item()

# Note: This doesn't have a test_ prefix because pytest can't run this
# directly because it takes a database as its input. Instead, it has
# to be called by each of the later tests.
def empty_database_is_empty(db):
    "Assert that everything is empty in a fresh DB."

    # Empty lists and dicts are both false in Python so we need a
    # slightly verbose check of the type before checking for
    # emptiness. We defined functions earlier for this.
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

def mock_categories():
    "Fakes data structures that looks like the database category returns."
    faq_categories = []
    faq_category_names = {}

    moved_category_index = 0

    # We'll use enumerate() here due to the suggestion of Pylint. Note
    # that Python is 0-based and the SQL IDs are 1-based so an
    # addition has to be done.
    for i, category in enumerate(TEST_FAQ_CATEGORIES):
        if category == 'Grades':
            moved_category_index = i
        category_id = i + 1
        faq_categories.append({'id': category_id,
                               'category_name': category,
                               'priority' : 5 if category != 'Grades' else 1})
        faq_category_names[category] = category_id

    # Move the Grades category to the front, assuming it only shows up
    # 0 or 1 times, which should hold as long as the test data is
    # defined properly, with no duplicate name for "Grades".
    faq_categories.insert(0, faq_categories.pop(moved_category_index))

    # Now map the category ID to the category index for later use.
    # Note that ID 0 is going to remain None so there is one more ID
    # entry than category entry.
    faq_category_index = [None for category in faq_categories]
    faq_category_index.append(None)
    for i, category in enumerate(faq_categories):
        faq_category_index[category['id']] = i

    return faq_categories, faq_category_names, faq_category_index

def mock_database_users():
    "Fakes data structures that look like the database users as hash tables."
    return [{'id': 1,
             'name': 'Guest',
            'campus_id': '',
            'email': '',
            'is_admin': False},
            {'id': 2,
             'name': 'admin',
            'campus_id': "FAKEID1",
            'email': "admin@example.com",
            'is_admin': True}]

def mock_faq_entries(faq_categories, faq_category_names, faq_category_index, users):
    "Fakes data structures that look like the database FAQ Entries as hash tables."
    faq_entries = []
    moved_faq_entry_index = 0
    for i, entry in enumerate(TEST_FAQ):
        faq_question, faq_answer, faq_category = entry
        faq_id = i + 1
        faq_category_id = faq_category_names[faq_category]
        faq_category = faq_categories[faq_category_index[faq_category_id]]['category_name']
        author_id = 2
        if faq_category == 'Grades':
            moved_faq_entry_index = i
        faq_entries.append({'id': faq_id,
                            'question_text': faq_question,
                            'answer_text': faq_answer,
                            'category_id': faq_category_id,
                            'author_id': author_id,
                            'category' : faq_category,
                            'author' : users[author_id - 1]['name'],
                            'priority' : 5 if faq_category != 'Grades' else 1})

    # Move the FAQ entry with the Grades category to the front,
    # assuming it only shows up 0 or 1 times. It shows up only once
    # for the test data as it currently exists, but this will need to
    # be modified if the test data is changed in a way that violates
    # this assumption.
    faq_entries.insert(0, faq_entries.pop(moved_faq_entry_index))
    return faq_entries

def test_repr():
    "Test the ORM objects' printable/string representations."
    # User
    user = User(id = 1,
                campus_id = 'AAAAAA',
                email = 'bob@example.com',
                name = 'Bob',
                password = 'pass',
                is_admin = True)
    str(user) == "User(id=1, email='bob@example.com', name='Bob', password=b'******', is_admin=True)"

    # FAQCategory
    category = FAQCategory(id = 1,
                           category_name = 'Cat',
                           priority = 10,
                           is_removed = False)
    str(category) == "FAQCategory(id=1, category_name='Cat', priority=10, is_removed=False)"

    # FAQEntry, which depends on the previous two
    timestamp = datetime.now()
    entry = FAQEntry(id = 1,
                     question_text = 'Cat',
                     answer_text = 'Meow',
                     category_id = 1,
                     author_id = 1,
                     priority = 1,
                     timestamp = timestamp,
                     is_removed = False)
    str(entry) == "FAQEntry(id=1, question_text='Cat', answer_text='Meow', category_id=1, " \
        f"author_id=1, priority=1, timestamp={timestamp!r}, is_removed=False)"

def test_asdict():
    "Tests object.asdict() for ORM objects"
    # User
    user = User(id = 1,
                campus_id = 'AAAAAA',
                email = 'bob@example.com',
                name = 'Bob',
                password = 'pass',
                is_admin = True)
    user.asdict() == {'id': 1,
                      'campus_id': 'AAAAAA',
                      'email': 'bob@example.com',
                      'name': 'Bob',
                      'password': 'pass',
                      'is_admin': True}

    # FAQCategory
    category = FAQCategory(id = 1,
                           category_name = 'Cat',
                           priority = 10,
                           is_removed = False)
    category.asdict() == {'id': 1,
                          'category_name': 'Cat',
                          'priority': 10}

    # FAQEntry, which depends on the previous two
    timestamp = datetime.now()
    entry = FAQEntry(id = 1,
                     question_text = 'Cat',
                     answer_text = 'Meow',
                     category_id = 1,
                     author_id = 1,
                     priority = 1,
                     timestamp = timestamp,
                     is_removed = False)
    # Note: Manually do the joins because the DB ORM isn't active.
    entry.category = category
    entry.author = user
    entry.asdict() == {'id': 1,
                       'question_text': 'Cat',
                       'answer_text': 'Meow',
                       'category_id': 1,
                       'author_id': 1,
                       'priority': 1,
                       'timestamp': timestamp,
                       'is_removed': False}

def test_database_with_test_data_file():
    "Test the basics of the database via exposed AppDatabase methods."

    # Create, initialize, and ensure that the database is empty.
    db = create_db_and_initialize()
    empty_database_is_empty(db)

    # This inserts several users, categories, and FAQ entries, which
    # can then be verified based on our assumptions. This is done all
    # at once because the FAQEntries need Users and FAQCategories.
    fill_debug_database(db)

    # First, we assume that the categories are added in order and
    # become associated with an incrementing ID. Let's build the
    # same thing manually so we can compare.
    faq_categories, faq_category_names, faq_category_index = mock_categories()

    # Does the database match our assumptions for FAQ categories?
    assert db.faq_categories() == faq_categories
    assert db.faq_categories_by_name() == faq_category_names

    # The two users as defined in fill_debug_database, except now
    # defined as a list of dicts here.
    users = mock_database_users()

    # Compare the returned user dicts to the expected user dict.
    assert db.users() == users

    # We'll do the same thing with the entries that we did with the
    # categories, creating a dict that should be what we get when we
    # query the database.
    faq_entries = mock_faq_entries(faq_categories, faq_category_names, faq_category_index, users)

    # Now we'll check our assumptions. Note that we need to remove the
    # timestamp from the results because the time that it will return
    # is arbitrary so we can't match against it.
    db_faq_entries = db.faq_entries()
    for entry in db_faq_entries:
        entry.pop('timestamp', None)
    assert db_faq_entries == faq_entries

    # Let's do that again for a single item.
    db_faq_entries = db.faq_entry(3)
    for entry in db_faq_entries:
        entry.pop('timestamp', None)

    # We need to find the position for entry 3
    entry_3_position = 0
    for i, entry in enumerate(faq_entries):
        if entry['id'] == 3:
            entry_3_position = i
    assert db_faq_entries == [faq_entries[entry_3_position]]

    # Now let's take entries by their categories.
    categorized_entries = []
    for category in faq_categories:
        category_id = category['id']
        categorized_entries.append(db.faq_entries_by_category(category_id))

    # Every FAQ entry has one category so their sum should be the
    # total number of FAQ entries. This is probably fancier than it
    # should be, but pylint didn't like the more straightforward ways
    # to write this.
    assert reduce(lambda x, entries: x + len(entries), categorized_entries, 0) == len(TEST_FAQ)

# This test might make more sense as the first test because it is so
# simple, but it is the second test because it checks our assumption
# that every in-memory SQLite database is a fresh new database. This
# assumption must hold for these tests to make sense.
#
# Importantly, this should go *before* testing the deletion of
# entries, too, because the database doesn't have to be fresh to be
# empty.
def test_empty_database():
    "Is a fresh database empty?"
    db = create_db_and_initialize()
    empty_database_is_empty(db)

def test_deleting_entries():
    "Test deleting entries from the database."

    # To keep things simple, let's fill it the same way again.
    db = create_db_and_initialize()
    empty_database_is_empty(db)
    fill_debug_database(db)

    # Let's make sure that our assumptions about the nature of the
    # test data aren't violated.
    assert len(TEST_FAQ) >= 5

    # Now let's remove entry 3.
    db.remove_faq_entry(3)

    # Note that removed entries are hidden even before being deleted.
    faq_entries = [entry['id'] for entry in db.faq_entries()]
    assert len(faq_entries) == len(TEST_FAQ) - 1

    assert 3 not in faq_entries
    assert 5 in faq_entries

    # Now let's delete entry 3.
    assert [entry['id'] for entry in db.delete_marked_entries()] == [3]

    # Let's repeat it again with 1 and 5.
    db.remove_faq_entry(1)
    db.remove_faq_entry(5)

    faq_entries = [entry['id'] for entry in db.faq_entries()]

    assert len(faq_entries) == len(TEST_FAQ) - 3
    assert 1 not in faq_entries
    assert 5 not in faq_entries

    # Order doesn't matter so we're going to check them separately
    # because it could be [1, 5] or [5, 1]
    marked_entries = [entry['id'] for entry in db.delete_marked_entries()]
    assert len(marked_entries) == 2
    assert 1 in marked_entries
    assert 5 in marked_entries

def test_deleting_all_entries():
    "Test deleting every entry from the database."

    # Create a DB the same number of entries as the length of TEST_FAQ
    db = create_db_and_initialize()
    fill_debug_database(db)
    assert len(db.faq_entries()) == len(TEST_FAQ)

    # Remove every single entry and make sure they are all removed.
    # Note, again, the off-by-one between Python indexing and the
    # entry IDs.
    for i in range(len(TEST_FAQ)):
        db.remove_faq_entry(i + 1)
    assert len(db.faq_entries()) == 0

    # Make sure that every single entry ID is returned as deleted.
    marked_entries = [entry['id'] for entry in db.delete_marked_entries()]
    assert len(marked_entries) == len(TEST_FAQ)
    marked_entries.sort()
    for i, faq_id in enumerate(marked_entries):
        assert i + 1 == faq_id
    assert len(db.faq_entries()) == 0
