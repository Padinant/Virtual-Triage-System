"""
Provides an API to write the chatbot history to logfiles.

Note that this just generates files. Displaying and managing these
files was not a priority feature of this class project.
"""

# prefix with timestamp and then UUID
def generate_unique_filename():
    "Generates a unique filename for the log."
    return "This is a stub for now."

def write_log_item(path, text):
    "Writes some text to a log file."
    with open(path, mode='a', encoding='utf8') as logfile:
        logfile.write(text)
        logfile.write('\n')

def write_log_entry(path, timestamp, question, answer):
    """
    Writes a timestamp, a question, and an answer. For human
    readability, these are separated by extra newlines. For machine
    readability, these newlines have hidden ASCII "group separator"
    and "record separator" characters.
    """
    # group separator and timestamp
    write_log_item(path, '\n\u001D\n')
    write_log_item(path, timestamp)
    # record separator and question
    write_log_item(path, '\n\u001E\n')
    write_log_item(path, question)
    # record separator and answer
    write_log_item(path, '\n\u001E\n')
    write_log_item(path, answer)
