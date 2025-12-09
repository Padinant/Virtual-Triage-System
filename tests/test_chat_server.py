"""
Tests the chatbot server implementation.
"""

from vts.chat_server import split_whitespace, split_long_line

def test_whitespace_split():
    "Tests the whitespace-based splitting."
    # Split in the right half.
    left, right, status = split_whitespace('This is a test of the ' \
                                           'whitespace splitting function.',
                                                    15)
    assert left == 'This is a test of the whitespace'
    assert right == 'splitting function.'
    assert status is True

    # Split in the left half.
    left, right, status = split_whitespace('This is a test of the ' \
                                           'whitespacesplittingfunction.',
                                                    15)
    assert left == 'This is a test of the'
    assert right == 'whitespacesplittingfunction.'
    assert status is True

    # Do not split.
    left, right, status = split_whitespace('This is a test', 15)
    assert left == 'This is a test'
    assert right is None
    assert status is True

    # Cannot split.
    left, right, status = split_whitespace('whitespacesplittingfunction', 15)
    assert left == 'whitespacesplittingfunction'
    assert right is None
    assert status is False

def test_long_line_split():
    "Tests splitting long lines into lists of strings."
    # Blank line.
    result = split_long_line('', 42)
    assert result == ['']

    # Short line.
    result = split_long_line('Hello.', 42)
    assert result == ['Hello.']

    # Short limit.
    result = split_long_line('This is a test of the whitespace splitting function.', 15)
    # First test our assumptions on type and length.
    for item in result:
        assert isinstance(item, str) and len(item) < 15
    # Then test our expected split.
    assert result == ['This is a', 'test of', 'the whitespace', 'splitting', 'function.']

    # Long limit.
    result = split_long_line('This is a test of the whitespace splitting function.', 45)
    # First test our assumptions on type and length.
    for item in result:
        assert isinstance(item, str) and len(item) < 45
    # Then test our expected split.
    assert result == ['This is a test of the whitespace', 'splitting function.']

    # Very long limit.
    result = split_long_line('This is a test of the whitespace splitting function.', 70)
    assert result == ['This is a test of the whitespace splitting function.']

    # Truncation is necessary.
    result = split_long_line('Thisisatestofthewhitespacesplittingfunction.', 15)
    assert len(result) == 1 and isinstance(result[0], str) and len(result[0]) == 15 - 1
    assert result == ['Thisisatestoft']
