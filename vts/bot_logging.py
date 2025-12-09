"""
Provides an API to write the chatbot history to logfiles.

Note that this just generates files. Displaying and managing these
files was not a priority feature of this class project.
"""

from datetime import datetime

import os

from xdg_base_dirs import xdg_data_home

def write_log_item(full_path, text):
    "Writes some text to a log file."
    with open(full_path, mode='a', encoding='utf8') as logfile:
        logfile.write(text)
        logfile.write('\n')

def write_log_entry(path, question, answer):
    """
    Writes a timestamp, a question, and an answer.
    """

    # Find the log directory and create it if it doesn't exist.
    log_dir = os.path.join(xdg_data_home(), "vts/")
    try:
        os.makedirs(log_dir)
    except OSError:
        pass

    # The path is relative to the log dir, probably a single file.
    log_path = os.path.join(log_dir, path)

    # Serialize the structured data (probably dicts) to the file as
    # plain text.
    write_log_item(log_path,
                   f'[{str(datetime.now())!r}, ' \
                   f'{question!r}, ' \
                   f'{answer!r}]')
