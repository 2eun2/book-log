from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime,
    ForeignKey, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_books = relationship("UserBook", back_populates="user", cascade="all, delete-orphan")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(30), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    authors = Column(String(255))
    publisher = Column(String(100))
    thumbnail = Column(String(500))
    genre = Column(String(50), nullable=True)

    user_books = relationship("UserBook", back_populates="book")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)


class UserBookTag(Base):
    __tablename__ = "user_book_tags"

    user_book_id = Column(Integer, ForeignKey("user_books.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    tag = relationship("Tag")


class UserBook(Base):
    __tablename__ = "user_books"
    __table_args__ = (
        UniqueConstraint("user_id", "book_id", name="uq_user_book"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    status = Column(String(20), nullable=False, default="want")  # want / reading / done
    rating = Column(Integer, nullable=True)  # 1~5
    review = Column(Text, nullable=True)
    started_at = Column(Date, nullable=True)
    finished_at = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="user_books")
    book = relationship("Book", back_populates="user_books")
    tags = relationship("UserBookTag", cascade="all, delete-orphan")
