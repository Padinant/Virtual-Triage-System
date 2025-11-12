"""
This file is designed to help reduce the chance of merge conflicts in
website.py during pull requests. This file contains some of the code
that is needed by the frontend files (HTML, CSS, etc.) to complete the
templating.
"""

# student/guest menu items
MENU_ITEMS = [
    {"name": "Home", "url": "/"},
    {"name": "Browse FAQ", "url": "/faq-search.html"},
    {"name": "Ask Chatbot", "url": "/chat.html"},
    {"name": "Contact Us", "url": "https://www.csee.umbc.edu/contact/"},
    {"name": "Department Website", "url": "https://www.csee.umbc.edu/"},
    {"name": "How to Use This Tool", "url": "#"}
]

# admin menu items
ADMIN_ITEMS = [
    {"name": "DEBUG Admin FAQ", "url": "/admin-login.html"},
]
