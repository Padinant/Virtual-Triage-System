"""
This is the object-relational mapping (ORM) of Python classes to the
database tables.
"""

from datetime import datetime
from enum import Enum

# Imports for the SQL tables
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import URL
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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
    password: Mapped[str] = mapped_column(String(60))
    is_admin: Mapped[bool] = mapped_column(Boolean)

    # Note: We don't want password hashes in our logs.
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, " \
            f"campus_id={self.campus_id!r}, " \
            f"email={self.email!r}, " \
            f"name={self.name!r}, " \
            f"password=b'******', " \
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
    priority: Mapped[int] = mapped_column(Integer, default=5)
    # Mark category as removed before batch deletion.
    is_removed: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"FAQCategory(id={self.id!r}, " \
            f"category_name={self.category_name!r}, " \
            f"priority={self.priority!r}, " \
            f"is_removed={self.is_removed!r})"

    def asdict(self) -> dict:
        "Turn the object into a key/value dictionary for APIs that expect this."
        return {'id': self.id,
                'category_name': self.category_name,
                'priority': self.priority}

# Note: Pylint isn't smart enough for all of the magic that is
# happening in this class with SQLAlchemy once relationships() are
# added to it.
#
# pylint:disable=unsubscriptable-object
class FAQEntry(Base):
    """
    FAQ entry database table.
    """
    __tablename__ = "faq_entry"

    author: Mapped["User"] = relationship()
    category: Mapped["FAQCategory"] = relationship()

    id: Mapped[int] = mapped_column(primary_key=True)
    question_text: Mapped[str] = mapped_column(String(500))
    answer_text: Mapped[str] = mapped_column(String(20000))
    category_id: Mapped[int] = mapped_column(ForeignKey("faq_category.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    priority: Mapped[int] = mapped_column(Integer, default=5)
    # Note: Pylint isn't smart enough to handle SQLAlchemy magic here.
    # It wants to use the invalid func.now instead of func.now()
    #
    # pylint:disable-next=not-callable
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    # Mark entry as removed before batch deletion.
    is_removed: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"FAQEntry(id={self.id!r}, " \
            f"question_text={self.question_text!r}, " \
            f"answer_text={self.answer_text!r}, " \
            f"category_id={self.category_id!r}, " \
            f"author_id={self.author_id!r}, " \
            f"priority={self.priority!r}, " \
            f"timestamp={self.timestamp!r}, " \
            f"is_removed={self.is_removed!r})"

    def asdict(self) -> dict:
        "Turn the object into a key/value dictionary for APIs that expect this."
        return {'id': self.id,
                'question_text': self.question_text,
                'answer_text': self.answer_text,
                'category_id': self.category_id,
                'author_id': self.author_id,
                'category' : self.category.category_name,
                'author' : self.author.name,
                'priority' : self.priority,
                'timestamp': self.timestamp}

# Application Representation of the Database

class Engine(Enum):
    """
    A representation of which DB engine is in use.
    """
    SQLITE_MEMORY = 1
    SQLITE_FILE = 2
    POSTGRESQL = 3

# Note: A secure way to store the database password will be needed.
def create_postgres_url(username: str,
                        password: str,
                        host: str = 'localhost') -> URL:
    "Creates the database URL for PostgreSQL."
    return URL.create('postgresql',
                      username=username,
                      password=password,
                      host=host,
                      database='umbc-triage')

def results_as_dicts(results) -> list[dict]:
    "Turn database results into a simple format for the frontend."
    return [result.asdict() for result in results]

def delete_marked_items(engine, table):
    "Deletes the items of the table that are marked for deletion."
    with Session(engine) as session:
        # Note: Pylint's style suggestion here doesn't work with SQLAlchemy's .where()
        # pylint:disable-next=singleton-comparison
        statement = delete(table).where(table.is_removed == True)
        statement = statement.returning(table.id)
        result_ids = [{'id': result} for result in session.scalars(statement)]
        session.commit()
        return result_ids

class AppDatabase():
    """
    The application database.

    Instantiate this class to call methods on it to retrieve data from
    the database.
    """
    path = ''
    def __init__(self, engine, username='', password='', host=False):
        self.engine_type = engine
        if engine == Engine.SQLITE_MEMORY:
            self.engine_path = "sqlite://"
        elif engine == Engine.SQLITE_FILE:
            if AppDatabase.path == '':
                self.engine_path = "sqlite:///test.db"
            else:
                self.engine_path = "sqlite:///" + AppDatabase.path
        elif engine == Engine.POSTGRESQL:
            if host:
                self.engine_path = create_postgres_url(username, password, host)
            else:
                self.engine_path = create_postgres_url(username, password)
        self.engine = create_engine(self.engine_path, echo=True)

    def initialize_metadata(self):
        "Create all of the ORM table metadata for a brand new database."
        Base.metadata.create_all(self.engine)

    def generate_password_hash(self, password, pwhash):
        "Use the pwhash object to generate a password hash of password."
        return pwhash.generate_password_hash(password)

    def users(self) -> list[dict]:
        "Turns a list of all users into dicts that can then be turned into JSON automatically."
        with Session(self.engine) as session:
            statement = select(User)
            return results_as_dicts(session.scalars(statement))

    def check_user_login(self, username: str, password: str, pwhash) -> bool:
        "Verifies that the password matches for the given username, checked by pwhash."
        with Session(self.engine) as session:
            statement = select(User).where(User.name == username)
            result = session.scalars(statement)
            user = result.one_or_none()
            # The username doesn't exist or the user has had
            # permissions removed.
            if user is None or not user.is_admin:
                return False
            return pwhash.check_password_hash(user.password, password)

    def add_item(self, item: User|FAQCategory|FAQEntry) -> int:
        "Uses a session to add and commit exactly one item to the database."
        with Session(self.engine) as session:
            session.add(item)
            session.commit()
            return item.id

    def add_items(self, items: list[User|FAQCategory|FAQEntry]):
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

    def faq_entry(self, faq_id: int) -> list[dict]:
        "Retrieves exactly one FAQ entry, specified by its ID."
        with Session(self.engine) as session:
            statement = select(FAQEntry).where(FAQEntry.id == faq_id)
            # Note: Pylint's style suggestion here doesn't work with SQLAlchemy's .where()
            # pylint:disable-next=singleton-comparison
            statement = statement.where(FAQEntry.is_removed == False)
            statement = statement.order_by(FAQEntry.priority)
            return results_as_dicts(session.scalars(statement))

    def faq_entries(self) -> list[dict]:
        "Retrieves all of the FAQ entries."
        with Session(self.engine) as session:
            # Note: Pylint's style suggestion here doesn't work with SQLAlchemy's .where()
            # pylint:disable-next=singleton-comparison
            statement = select(FAQEntry).where(FAQEntry.is_removed == False)
            statement = statement.order_by(FAQEntry.priority)
            return results_as_dicts(session.scalars(statement))

    def remove_faq_entry(self, faq_id: int) -> bool:
        "Marks an FAQ entry with the given ID as removed."
        def query(statement):
            return statement.where(FAQEntry.id == faq_id)

        def update(item):
            item.is_removed = True

        self.update_item(query, update)

        return True

    def is_empty_category(self, category_id: int) -> bool:
        "Checks to make sure that the category is empty."
        faq_entries = self.faq_entries_by_category(category_id)
        return len(faq_entries) == 0

    def remove_category(self, category_id: int) -> bool:
        """
        Marks a category with the given ID as removed. Returns True if
        the category can be removed and False if the category cannot
        be removed. A category in use cannot be removed.
        """
        if not self.is_empty_category(category_id):
            return False

        with Session(self.engine) as session:
            statement = select(FAQCategory).where(FAQCategory.id == category_id)
            result = session.scalars(statement).one()
            result.is_removed = True
            session.commit()

        return True

    def faq_entries_by_category(self, category_id: int) -> list[dict]:
        "Retrieves the FAQ entries with the given category (excludes removed entries)."
        with Session(self.engine) as session:
            statement = select(FAQEntry).where(FAQEntry.category_id == category_id)
            # Note: Pylint's style suggestion here doesn't work with SQLAlchemy's .where()
            # pylint:disable-next=singleton-comparison
            statement = statement.where(FAQEntry.is_removed == False)
            statement = statement.order_by(FAQEntry.priority)
            return results_as_dicts(session.scalars(statement))

    def faq_categories(self) -> list[dict]:
        "Retrieves all FAQ categories."
        with Session(self.engine) as session:
            # Note: Pylint's style suggestion here doesn't work with SQLAlchemy's .where()
            # pylint:disable-next=singleton-comparison
            statement = select(FAQCategory).where(FAQCategory.is_removed == False)
            statement = statement.order_by(FAQCategory.priority)
            return results_as_dicts(session.scalars(statement))

    def faq_categories_by_name(self) -> dict:
        "Returns a dict of category names, associating them with their internal IDs."
        categories = {}
        with Session(self.engine) as session:
            # Note: Pylint's style suggestion here doesn't work with SQLAlchemy's .where()
            # pylint:disable-next=singleton-comparison
            statement = select(FAQCategory).where(FAQCategory.is_removed == False)
            for category in session.scalars(statement):
                categories[category.category_name] = category.id
        return categories

    def category_name_exists(self, category_name: str) -> bool:
        """
        Check if a category name already exists (case-insensitive).
        Returns True if the name exists, False otherwise.
        """
        with Session(self.engine) as session:
            # Note: Pylint's style suggestion here doesn't work with SQLAlchemy's .where()
            # pylint:disable-next=singleton-comparison
            statement = select(FAQCategory).where(FAQCategory.is_removed == False)
            categories = session.scalars(statement)
            for category in categories:
                if category.category_name.lower() == category_name.lower():
                    return True
        return False

    def update_category(self,
                        category_id: int,
                        new_name: str,
                        new_priority) -> bool:
        """
        Update the name of a category specified by `category_id`.
        Returns True on success.
        """
        with Session(self.engine) as session:
            statement = select(FAQCategory).where(FAQCategory.id == category_id)
            result = session.scalars(statement).one()
            result.category_name = new_name
            result.priority = new_priority
            session.commit()
        return True

    def delete_marked_entries(self):
        "Deletes the entries that have been marked for deletion."
        return delete_marked_items(self.engine, FAQEntry)

    def delete_marked_categories(self):
        "Deletes the categories that have been marked for deletion."
        return delete_marked_items(self.engine, FAQCategory)
