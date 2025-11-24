"""
Test the parts of website.py that are best tested through code instead
of through stepping through every web page. This may change in the
final sprint.

Note that for Sprint 2, only the non-Flask functions are tested here.
"""

from markdown import markdown

from vts.test_data import TEST_FAQ
from vts.website import faq_entries_to_markdown
from vts.website import faq_titles_to_markdown

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
