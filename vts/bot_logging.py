"""
Provides an API to write the chatbot history to logfiles.

Note that this just generates files. Displaying and managing these
files was not a priority feature of this class project.
"""

from datetime import datetime

def write_log_item(path, text):
    "Writes some text to a log file."
    with open(path, mode='a', encoding='utf8') as logfile:
        logfile.write(text)
        logfile.write('\n')

def write_log_entry(path, question, answer):
    """
    Writes a timestamp, a question, and an answer.
    """
    write_log_item(path,
                   f'[{str(datetime.now())!r}, ' \
                   f'{question!r}, ' \
                   f'{answer!r}]')
