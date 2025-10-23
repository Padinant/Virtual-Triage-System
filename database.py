"""
This is the object-relational mapping (ORM) of Python classes to the
database tables.
"""

from enum import Enum

# Imports for the SQL tables
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
# Imports for the SQL database itself
from sqlalchemy import create_engine
from sqlalchemy import select
from sqlalchemy.orm import Session

# ORM Database Tables/Classes

# Note: Every class must have a __repr__ printable representation
# method (for debugging or logging) and a to_json method.
#
# Pylint will complain if a class has fewer than two methods.

class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base class.
    """

    def __repr__(self) -> str:
        return "Base()"

    def to_json(self) -> str:
        "Converts the database row to a JSON object."
        return "{}"

class User(Base):
    """
    User account database table.
    """
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    campus_id: Mapped[str] = mapped_column(String(10))
    email: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(50))
    is_admin: Mapped[bool] = mapped_column(Boolean)
    # Also associate chat history?

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, " \
            f"campus_id={self.campus_id!r}, " \
            f"email={self.email!r}, " \
            f"name={self.name!r}, " \
            f"is_admin={self.is_admin!r})"

    def to_json(self) -> str:
        "Converts the database row to a JSON object."
        admin_status = "true" if self.is_admin else "false"
        return f'{{"id" : {self.id!r}, ' \
            f'"campus_id" : "{self.campus_id}", ' \
            f'"email" : "{self.email}", ' \
            f'"name" : "{self.name}", ' \
            f'"is_admin" : {admin_status}}}'

class FAQCategory(Base):
    """
    FAQ category/tag database table.
    """
    __tablename__ = "faq_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(String(50))

    def __repr__(self) -> str:
        return f"FAQCategory(id={self.id!r}, " \
            f"category_name={self.category_name!r})"

    def to_json(self) -> str:
        "Converts the database row to a JSON object."
        return f'{{"id" : {self.id!r}, ' \
            f'"campus_id" : "{self.category_name}"}}' \

class FAQEntry(Base):
    """
    FAQ entry database table.
    """
    __tablename__ = "faq_entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_text: Mapped[str] = mapped_column(String(500))
    answer_text: Mapped[str] = mapped_column(String(20000))
    category_id: Mapped[int] = mapped_column(ForeignKey("faq_category.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    def __repr__(self) -> str:
        return f"FAQEntry(id={self.id!r}, " \
            f"question_text={self.question_text!r}" \
            f"answer_text={self.answer_text!r}" \
            f"category_id={self.category_id!r}" \
            f"author_id={self.author_id!r})"

    def to_json(self) -> str:
        "Converts the database row to a JSON object."
        return f'{{"id" : {self.id!r}, ' \
            f'"question_text" : "{self.question_text}", ' \
            f'"answer_text" : "{self.answer_text}", ' \
            f'"category_id" : {self.category_id}, ' \
            f'"author_id" : {self.author_id}}}'

# Application Representation of the Database

class Engine(Enum):
    """
    A representation of which DB engine is in use.
    """
    SQLITE_MEMORY = 1
    SQLITE_FILE = 2
    POSTGRESQL = 3

class AppDatabase():
    """
    The application database.
    """
    def __init__(self, engine):
        self.engine_type = engine
        if engine == Engine.SQLITE_MEMORY:
            self.engine_path = "sqlite://"
        elif engine == Engine.SQLITE_FILE:
            self.engine_path = "sqlite:///instance/test.db"
        # TODO: fixme: implement this for postgres for early merge
        elif engine == Engine.POSTGRESQL:
            # Not yet implemented.
            raise TypeError
        self.engine = create_engine(self.engine_path, echo=True)

# Note: We will use PostgreSQL in production.
def create_debug_database(engine_type):
    "Creates the debug database and populates it with the entries above."
    db = AppDatabase(engine_type)
    Base.metadata.create_all(db.engine)
    return db.engine

def get_debug_database(is_in_memory):
    "Creates an interface to the already-existing database."
    if is_in_memory:
        engine_type = Engine.SQLITE_MEMORY
    else:
        engine_type = Engine.SQLITE_FILE
    db = AppDatabase(engine_type)
    return db.engine

def print_all_users(engine):
    "Prints all of the database's users to assist in debugging and testing."
    with Session(engine) as session:
        statement = select(User)
        for user in session.scalars(statement):
            print(user)

def users_to_json(engine):
    "Turns a list of all users into JSON to assist in debugging and testing."
    with Session(engine) as session:
        statement = select(User)
        json_users = [user.to_json() for user in session.scalars(statement)]
        return '[' + ','.join(json_users) + ']'

def get_faq_entries(engine):
    "Retrieves the FAQ entries as markdown."
    with Session(engine) as session:
        statement = select(FAQEntry)
        return [(entry.question_text, entry.answer_text)
                for entry in session.scalars(statement)]
