"""
Tests the chatbot server implementation.
"""

from vts.chat_server import split_whitespace

def test_whitespace_split():
    "Tests the whitespace-based splitting."
    left, right, status = split_whitespace('This is a test of the ' \
                                                    'whitespace splitting function.',
                                                    15)
    assert left == 'This is a test of the whitespace'
    assert right == 'splitting function.'
    assert status is True

    left, right, status = split_whitespace('This is a test of the ' \
                                                    'whitespacesplittingfunction.',
                                                    15)
    assert left == 'This is a test of the'
    assert right == 'whitespacesplittingfunction.'
    assert status is True

    left, right, status = split_whitespace('This is a test', 15)
    assert left == 'This is a test'
    assert right is None
    assert status is True

    left, right, status = split_whitespace('whitespacesplittingfunction', 15)
    assert left == 'whitespacesplittingfunction'
    assert right is None
    assert status is False
