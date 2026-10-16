from fastapi import FastAPI
import models
from database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="book-log")

@app.get("/")
def read_root():
    return {"message": "Hello, book-log"}