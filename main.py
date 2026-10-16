from typing import Optional
import requests
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from auth import create_access_token, get_current_user, hash_password, verify_password
from database import engine, get_db
from kakao import search_books

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="book-log")


@app.get("/")
def read_root():
    return {"message": "Hello, book-log"}


@app.post("/auth/signup", response_model=schemas.UserResponse, status_code=201)
def signup(req: schemas.SignupRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == req.email).first():
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")

    user = models.User(
        email=req.email,
        password_hash=hash_password(req.password),
        nickname=req.nickname,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/auth/login", response_model=schemas.TokenResponse)
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    return schemas.TokenResponse(access_token=create_access_token(user.id))

@app.get("/books/search")
def books_search(q: str, page: int = 1):
    try:
        return search_books(q, page)
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="도서 검색 서버에 연결하지 못했습니다.")

@app.post("/me/books", response_model=schemas.UserBookResponse, status_code=201)
def add_my_book(
    req: schemas.AddBookRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    # 1) books 테이블에 없으면 저장 (같은 책은 한 번만)
    book = db.query(models.Book).filter(models.Book.isbn == req.isbn).first()
    if not book:
        book = models.Book(
            isbn=req.isbn,
            title=req.title,
            authors=req.authors,
            publisher=req.publisher,
            thumbnail=req.thumbnail,
        )
        db.add(book)
        db.flush()

    # 2) 이미 내 서재에 있는지 확인
    exists = (
        db.query(models.UserBook)
        .filter(models.UserBook.user_id == user.id, models.UserBook.book_id == book.id)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="이미 서재에 있는 책입니다.")

    user_book = models.UserBook(user_id=user.id, book_id=book.id, status=req.status)
    db.add(user_book)
    db.commit()
    db.refresh(user_book)
    return user_book


@app.get("/me/books", response_model=list[schemas.UserBookResponse])
def list_my_books(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    query = db.query(models.UserBook).filter(models.UserBook.user_id == user.id)
    if status:
        query = query.filter(models.UserBook.status == status)
    return query.order_by(models.UserBook.created_at.desc()).all()


@app.patch("/me/books/{user_book_id}", response_model=schemas.UserBookResponse)
def update_my_book(
    user_book_id: int,
    req: schemas.UpdateBookRequest,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    user_book = (
        db.query(models.UserBook)
        .filter(models.UserBook.id == user_book_id, models.UserBook.user_id == user.id)
        .first()
    )
    if not user_book:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")

    if req.rating is not None and not 1 <= req.rating <= 5:
        raise HTTPException(status_code=400, detail="별점은 1~5 사이여야 합니다.")

    for field, value in req.model_dump(exclude_unset=True).items():
        setattr(user_book, field, value)

    db.commit()
    db.refresh(user_book)
    return user_book


@app.delete("/me/books/{user_book_id}", status_code=204)
def delete_my_book(
    user_book_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    user_book = (
        db.query(models.UserBook)
        .filter(models.UserBook.id == user_book_id, models.UserBook.user_id == user.id)
        .first()
    )
    if not user_book:
        raise HTTPException(status_code=404, detail="기록을 찾을 수 없습니다.")

    db.delete(user_book)
    db.commit()