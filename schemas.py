from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    nickname: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

from datetime import date
from typing import Optional


class AddBookRequest(BaseModel):
    isbn: str
    title: str
    authors: str = ""
    publisher: str = ""
    thumbnail: str = ""
    status: str = "want"  # want / reading / done


class UpdateBookRequest(BaseModel):
    status: Optional[str] = None
    rating: Optional[int] = None
    review: Optional[str] = None
    started_at: Optional[date] = None
    finished_at: Optional[date] = None


class BookInfo(BaseModel):
    isbn: str
    title: str
    authors: Optional[str] = None
    publisher: Optional[str] = None
    thumbnail: Optional[str] = None

    class Config:
        from_attributes = True


class UserBookResponse(BaseModel):
    id: int
    status: str
    rating: Optional[int] = None
    review: Optional[str] = None
    started_at: Optional[date] = None
    finished_at: Optional[date] = None
    book: BookInfo

    class Config:
        from_attributes = True