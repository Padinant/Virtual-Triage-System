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
    {"name": "How to Use This Tool", "url": "/how-to.html"}
]

def category_page_title(category_id, name):
    "Generates the category page title string."
    return f"FAQ Category #{category_id} - {name} - Interactive Help"

TITLES = {"main-page": "Interactive Help - UMBC Computer Science & Electrical Engineering",
          "how-to": "How to Use This Tool - Interactive Help",
          "admin-faq-search": "Admin FAQ Management - Interactive Help",
          "admin-faq-add": "Add New FAQ - Admin",
          "admin-faq-edit": lambda faq_id : f"Edit FAQ #{faq_id} - Admin",
          "admin-faq-remove": lambda faq_id : f"Remove FAQ #{faq_id} - Admin",
          "admin-category": "Admin Category Management - Interactive Help",
          "admin-category-add": "Add New Category - Admin",
          "admin-category-edit": lambda category_id : f"Edit Category #{category_id} - Admin",
          "admin-category-remove": lambda category_id : f"Remove Category #{category_id} - Admin",
          "faq-search": "Browse FAQ - Interactive Help",
          "faq-item": lambda faq_id : f"FAQ Item #{faq_id} - Interactive Help",
          "category-page": category_page_title,
          "admin-login": "Admin Login - Interactive Help",
          "chatbot": "Ask Chatbot - Interactive Help"}
