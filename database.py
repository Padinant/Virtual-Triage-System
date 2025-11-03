"""
This is the object-relational mapping (ORM) of Python classes to the
database tables.
"""

from enum import Enum

# Imports for the SQL tables
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import URL
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
# Imports for the SQL database itself
from sqlalchemy import create_engine
from sqlalchemy import delete
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

    def asdict(self) -> dict:
        "Turn the object into a key/value dictionary for APIs that expect this."
        return {}

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

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, " \
            f"campus_id={self.campus_id!r}, " \
            f"email={self.email!r}, " \
            f"name={self.name!r}, " \
            f"is_admin={self.is_admin!r})"

    def asdict(self) -> dict:
        "Turn the object into a key/value dictionary for APIs that expect this."
        return {'id': self.id,
                'campus_id': self.campus_id,
                'email': self.email,
                'name': self.name,
                'is_admin': self.is_admin}

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

    def asdict(self) -> dict:
        "Turn the object into a key/value dictionary for APIs that expect this."
        return {'id': self.id,
                'category_name': self.category_name}

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
    # Deleted FAQ entries are first marked as removed and then can be
    # batch deleted later on.
    is_removed: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"FAQEntry(id={self.id!r}, " \
            f"question_text={self.question_text!r}" \
            f"answer_text={self.answer_text!r}" \
            f"category_id={self.category_id!r}" \
            f"author_id={self.author_id!r}" \
            f"is_removed={self.is_removed!r})"

    def asdict(self) -> dict:
        "Turn the object into a key/value dictionary for APIs that expect this."
        return {'id': self.id,
                'question_text': self.question_text,
                'answer_text': self.answer_text,
                'category_id': self.category_id,
                'author_id': self.author_id}

# Application Representation of the Database

class Engine(Enum):
    """
    A representation of which DB engine is in use.
    """
    SQLITE_MEMORY = 1
    SQLITE_FILE = 2
    POSTGRESQL = 3

# Note: A secure way to store the database password will be needed.
def create_postgres_url(username, password, host='localhost'):
    "Creates the database URL for PostgreSQL."
    return URL.create('postgresql',
                      username=username,
                      password=password,
                      host=host,
                      database='umbc-triage')

def results_as_dicts(results) -> list[dict]:
    "Turn database results into a simple format for the frontend."
    return [result.asdict() for result in results]

class AppDatabase():
    """
    The application database.

    Instantiate this class to call methods on it to retrieve data from
    the database.
    """
    def __init__(self, engine, username='', password=''):
        self.engine_type = engine
        if engine == Engine.SQLITE_MEMORY:
            self.engine_path = "sqlite://"
        elif engine == Engine.SQLITE_FILE:
            self.engine_path = "sqlite:///instance/test.db"
        elif engine == Engine.POSTGRESQL:
            self.engine_path = create_postgres_url(username, password)
        self.engine = create_engine(self.engine_path, echo=True)

    def initialize_metadata(self):
        "Create all of the ORM table metadata for a brand new database."
        Base.metadata.create_all(self.engine)

    def users_to_jsonable(self) -> list[dict]:
        "Turns a list of all users into dicts that can then be turned into JSON automatically."
        with Session(self.engine) as session:
            statement = select(User)
            return results_as_dicts(session.scalars(statement))

    def add_item(self, item):
        "Uses a session to add and commit exactly one item to the database."
        with Session(self.engine) as session:
            session.add(item)
            session.commit()
            return item.id

    def add_items(self, items):
        "Uses a session to add and commit a list of items to the database."
        with Session(self.engine) as session:
            session.add_all(items)
            session.commit()

    def update_item(self, query, update):
        """
        Update an item in a session through two higher order functions.

        The first function, query, takes a statement as its argument and lets the
        caller refine that statement, such as with a .where() method call.

        The second function, update, passes in an ORM object and lets
        the caller edit that object.

        The result is then committed.
        """
        with Session(self.engine) as session:
            statement = select(FAQEntry)
            statement = query(statement)
            result = session.scalars(statement).one()
            update(result)
            session.commit()

    def faq_entry(self, faq_id) -> list[dict]:
        "Retrieves exactly one FAQ entry, specified by its ID."
        with Session(self.engine) as session:
            statement = select(FAQEntry).where(FAQEntry.id == faq_id)
            # Note: Pylint's style suggestion here doesn't work with SQLAlchemy's .where()
            # pylint:disable-next=singleton-comparison
            statement = statement.where(FAQEntry.is_removed == False)
            return results_as_dicts(session.scalars(statement))

    def faq_entries(self) -> list[dict]:
        "Retrieves all of the FAQ entries."
        with Session(self.engine) as session:
            # Note: Pylint's style suggestion here doesn't work with SQLAlchemy's .where()
            # pylint:disable-next=singleton-comparison
            statement = select(FAQEntry).where(FAQEntry.is_removed == False)
            return results_as_dicts(session.scalars(statement))

    def remove_faq_entry(self, faq_id):
        "Marks an FAQ entry with the given ID as removed."
        def query(statement):
            return statement.where(FAQEntry.id == faq_id)

        def update(item):
            item.is_removed = True

        self.update_item(query, update)

    def faq_entries_by_category(self, category_id) -> list[dict]:
        "Retrieves the FAQ entries with the given category."
        with Session(self.engine) as session:
            statement = select(FAQEntry).where(FAQEntry.category_id == category_id)
            return results_as_dicts(session.scalars(statement))

    def faq_categories(self) -> list[dict]:
        "Retrieves all FAQ categories."
        with Session(self.engine) as session:
            statement = select(FAQCategory)
            return results_as_dicts(session.scalars(statement))

    def faq_categories_by_name(self) -> dict:
        "Returns a dict of category names, associating them with their internal IDs."
        categories = {}
        with Session(self.engine) as session:
            statement = select(FAQCategory)
            for category in session.scalars(statement):
                categories[category.category_name] = category.id
        return categories

    def delete_marked_entries(self):
        "Deletes the entries that have been marked for deletion."
        with Session(self.engine) as session:
            # Note: Pylint's style suggestion here doesn't work with SQLAlchemy's .where()
            # pylint:disable-next=singleton-comparison
            statement = delete(FAQEntry).where(FAQEntry.is_removed == True)
            statement = statement.returning(FAQEntry.id)
            result_ids = [{'id': result} for result in session.scalars(statement)]
            session.commit()
            return result_ids
