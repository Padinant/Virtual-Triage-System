"""
This module provides default sample FAQ questions to fill the website
with realistic data taken from our knowledge base.
"""

from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

from vts.database import User
from vts.database import FAQCategory
from vts.database import FAQEntry

FAQ = [("Why undergraduate programs are offered by the UMBC CSEE department?",
        "The UMBC CSEE department offers the following undergraduate programs:\n" \
        "1. Computer Science Major (Bachelor's of Science)\n" \
        "2. Computer Science Minor\n" \
        "3. Computer Engineering Major\n" \
        "4. Combined Computer Science BS/MS Program\n" \
        "5. Combined Computer Engineering BS/MS Program\n",
        "Undergraduate programs"),
       ("What does the UMBC CSEE department offer for its graduate programs?\n",
        "Our specialty areas are as follows:\n" \
        "- **Computer Science**: Artificial Intelligence, Machine Learning and Data Mining, " \
        " Multi-Agent Systems, Web 2.0, Wireless Sensor Networks, Graphics and Visualization, " \
        " Game Development.\n" \
        "- **Computer Engineering**: VLSI design and testing, VLSI arithmetic algorithms and " \
        "security, Mixed-signal VLSI, Distributed real-time, and embedded systems, Energy " \
        "efficient and high performance systems and Bioelectronics.\n" \
        "- **Electrical Engineering**: Communications, Signal processing, Microelectronics, " \
        "Sensor technology and Photonics.\n",
        "Graduate programs"),
       ("How do I request room swipe access?",
        "If you are **faculty or staff**, then you can fill out [this form]" \
        "(https://docs.google.com/forms/d/e/1FAIpQLScQs5QiJrMrFbYqA4PnOLEP2VfJc_" \
        "39EujAZEb3MU0P76RS2g/viewform?c=0&w=1).",
        "Resources"),
       ("How do I request room swipe access for something such as a research lab as a student?",
        "You should reach out via email or in person to the relevant CSEE faculty member " \
        "who is the reason for your request.",
        "Resources"),
       ("What is the contact information for the CSEE main office?",
        "The CSEE main office location is:\n\n```\n    ITE 325 1000 Hilltop Circle\n" \
        "    Baltimore, MD 21250\n```\n\n" \
        "Our phone number is 410-455-3500 and our email is dept@cs.umbc.edu\n",
        "Contact")]

FAQ_CATEGORIES = ["Undergraduate programs", "Graduate programs", "Resources", "Contact"]

def add_sample_questions(db, pwhash):
    "Fills the database with realistic sample questions."
    test_password = "password"
    if pwhash is not None:
        test_password = db.generate_password_hash(test_password, pwhash)
    # Note: This should be some sort of registration setup instead of
    # fake demo-specific information.
    admin = User(name = "admin",
                 campus_id = "ADMINID",
                 email = "admin@example.com",
                 is_admin = True,
                 password = test_password)

    db.add_item(admin)

    categories = [FAQCategory(category_name = category, priority = 5)
                  for category in FAQ_CATEGORIES]

    db.add_items(categories)

    category_dict = db.faq_categories_by_name()

    with Session(db.engine) as session:
        statement = select(User).where(User.name == "admin")
        admin_id = session.scalars(statement).first().id

        entries = [FAQEntry(question_text = question,
                        answer_text = answer,
                        category_id = category_dict[category],
                        author_id = admin_id,
                        priority = 5,
                        timestamp = datetime.now())
               for question, answer, category in FAQ]

    db.add_items(entries)
