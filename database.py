"""
This is the object-relational mapping (ORM) of Python classes to the
database tables.
"""

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

# Database Tables/Classes

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
        return f'{{"id" = {self.id!r}, ' \
            f'"campus_id" = "{self.campus_id}", ' \
            f'"email" = "{self.email}", ' \
            f'"name" = "{self.name}", ' \
            f'"is_admin" = {admin_status}}}'

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
        return f'{{"id" = {self.id!r}, ' \
            f'"campus_id" = "{self.category_name}"}}' \

class FAQEntry(Base):
    """
    FAQ entry database table.
    """
    __tablename__ = "faq_entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    title_text: Mapped[str] = mapped_column(String(200))
    body_text: Mapped[str] = mapped_column(String(20000))
    category_id: Mapped[int] = mapped_column(ForeignKey("faq_category.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    def __repr__(self) -> str:
        return f"FAQEntry(id={self.id!r}, " \
            f"title_text={self.title_text!r}" \
            f"body_text={self.body_text!r}" \
            f"category_id={self.category_id!r}" \
            f"author_id={self.author_id!r})"

    def to_json(self) -> str:
        "Converts the database row to a JSON object."
        return f'{{"id" = {self.id!r}, ' \
            f'"title_text" = "{self.title_text}", ' \
            f'"body_text" = "{self.body_text}", ' \
            f'"category_id" = {self.category_id}, ' \
            f'"author_id" = {self.author_id}}}'

# Database Functions

# Note: We will use PostgreSQL in production, but this uses in-memory
# SQLite for local testing.
def create_debug_database():
    "Creates the debug database and populates it with the entries above."
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)
    return engine

def fill_debug_database(engine):
    "Fills the debug database with fake data for testing."
    with Session(engine) as session:
        guest = User(name = "Guest",
                     campus_id = "",
                     email = "",
                     is_admin = False)
        admin = User(name = "Administrator",
                     campus_id = "FAKEID1",
                     email = "admin@example.com",
                     is_admin = True)
        category = FAQCategory(category_name = "Lorem Ipsum")
        #entry = FAQEntry()
        session.add_all([guest, admin, category])
        session.commit()

def print_all_users(engine):
    "Prints all of the database's users to assist in debugging and testing."
    with Session(engine) as session:
        statement = select(User)
        for user in session.scalars(statement):
            print(user)
