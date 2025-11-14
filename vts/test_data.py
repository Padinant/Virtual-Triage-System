# Note: sample data taken from
# https://www.csee.umbc.edu/undergraduate/undergraduate-faq-advising-registration-graduation/
# Another good FAQ candidate is https://www.csee.umbc.edu/undergraduate/computer-science-bs/faq/

"""
This module provides test data for the test database and other unit
tests.
"""

from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

# from vts.database import AppDatabase
from vts.database import User
from vts.database import FAQCategory
from vts.database import FAQEntry

# Takes one complicated question and three simple questions from an
# actual UMBC CSEE FAQ to simulate realistic data.
#
# Each FAQ item is a tuple of three entries: the question, the answer,
# and the category name.
TEST_FAQ = [("Why can't I register for my classes?",
             "1. **Have you been advised, and did your adviser clear you to register?** " \
             "All students must interact with their academic adviser each semester. Then, in " \
             "order for the student to register, the adviser has to give ‘advising clearance’ " \
             "in the SA system before the student can register.\n" \
             "2. **Is it too soon for you to be registering?** Students may register for classes " \
             "for the next semester only after a certain date called their ‘registration " \
             "appointment’. These dates can be found on the Registrar’s web site here: "\
             "[https://registrar.umbc.edu/academic-calendar/registration-appointments/]" \
             "(https://registrar.umbc.edu/academic-calendar/registration-appointments/)\n" \
             "Registration dates are based on earned credits (not total credits), and students " \
             "with more earned credits go first.\n" \
             "3. **Did you apply to graduate but not actually graduate?** If you apply to " \
             "graduate, you are automatically locked out of the registration system for future " \
             "semesters. If you applied but did not graduate, you need to contact the " \
             "Registrar’s Office and have them reactivate your account.\n" \
             "4. **Do you have a financial hold?** You cannot register for classes if you have " \
             "unpaid bills: this must be taken care of first.\n",
             "Registration"),
            ("Why can’t I register for a specific course?",
             "The course might require departmental consent, or you do not have all the " \
             "prerequisites for the course. Sometimes a course you transferred in, thinking it " \
             "qualifies as a prerequisite, may not have been deemed equivalent.\n",
             "Registration"),
            ("How do I get permission to enroll in a closed class?",
             "If a class is closed, then it has reached its capacity. You should select a " \
             "different class for your schedule. Exceptions may be made for students graduating " \
             "in the semester. See our [wait list " \
             "policy](https://www.csee.umbc.edu/files/2022/06/wait_list_policy.pdf) for more " \
             "information.\n",
             "Registration"),
            ("Do grades I receive when I take classes outside of UMBC count toward my GPA?",
             "Not usually. You receive credits toward the 120 credits needed to graduate (and " \
             "toward the 45 upper level credits needed if the course is upper level), but only " \
             "your grades in UMBC courses are used in your UMBC GPA calculation.\n",
             "Grades"),
            ("Can I take a course at a community college during my last semester?",
             "Yes, as long as you have not already transferred in the maximum of 60 credits " \
             "from a 2-year institution, and you will satisfy the requirement of 30 credits " \
             "taken at UMBC.\n",
             "Credits")]

TEST_FAQ_CATEGORIES = ["Registration", "Grades", "Credits"]

def fill_debug_database(db):
    "Fills the debug database with fake data for testing."
    # Store the users and FAQ categories first because their fields do
    # not use relations.
    guest = User(name = "Guest",
                 campus_id = "",
                 email = "",
                 is_admin = False,
                 password = b'')
    admin = User(name = "Administrator",
                 campus_id = "FAKEID1",
                 email = "admin@example.com",
                 is_admin = True,
                 password = b'password')
    categories = [FAQCategory(category_name = category)
                  for category in TEST_FAQ_CATEGORIES]
    db.add_items([guest, admin])
    db.add_items(categories)
    category_dict = db.faq_categories_by_name()
    # Find the first (and hopefully only) admin ID.
    with Session(db.engine) as session:
        statement = select(User).where(User.name == "Administrator")
        admin = session.scalars(statement).first()
        admin_id = admin.id
    # Add the FAQ entries by converting the constants' tuple format
    # into the object-oriented format and then committing it to the
    # database.
    entries = [FAQEntry(question_text = question,
                        answer_text = answer,
                        category_id = category_dict[category],
                        author_id = admin_id,
                        timestamp = datetime.now())
               for question, answer, category in TEST_FAQ]
    db.add_items(entries)
