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

class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base class.
    """

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

class FAQCategory(Base):
    """
    FAQ category/tag database table.
    """
    __tablename__ = "faq_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(String(50))

class FAQEntry(Base):
    """
    FAQ entry database table.
    """
    __tablename__ = "faq_entry"

    id: Mapped[int] = mapped_column(primary_key=True)
    title_text: Mapped[str] = mapped_column(String(50))
    body_text: Mapped[str] = mapped_column(String(20000))
    category_id: Mapped[int] = mapped_column(ForeignKey("faq_category.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

# Note: We will use PostgreSQL in production, but this uses in-memory
# SQLite for local testing.
def create_debug_database():
    "Creates the debug database and populates it with the entries above."
    engine = create_engine("sqlite://", echo=True)
    Base.metadata.create_all(engine)
