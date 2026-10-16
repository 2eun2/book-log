from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import requests
from kakao import search_books
import models
import schemas
from auth import create_access_token, hash_password, verify_password
from database import engine, get_db

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