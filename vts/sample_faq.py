# Sample questions that our knowledge base has the answers to.

"""
This module provides default sample FAQ questions to fill the website
with realistic data.
"""

from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select

from vts.database import User
from vts.database import FAQCategory
from vts.database import FAQEntry

def add_sample_questions(db, pwhash):
    "Fills the database with realistic sample questions."

