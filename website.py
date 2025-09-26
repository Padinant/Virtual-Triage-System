"""
Web server layer that serves HTML, CSS, JSON, etc.
"""

from flask import Flask
from flask import render_template
from database import create_debug_database

app = Flask(__name__)

create_debug_database()

@app.route("/")
def index():
    "The main entry point to the app."
    return render_template('index.html')

@app.route("/index.html")
def index():
    "Another name for the main entry point."
    return render_template('index.html')
