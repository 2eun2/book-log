import os

import requests
from dotenv import load_dotenv

load_dotenv()

KAKAO_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_BOOK_URL = "https://dapi.kakao.com/v3/search/book"


def search_books(query: str, page: int = 1, size: int = 10) -> list[dict]:
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": query, "page": page, "size": size}

    res = requests.get(KAKAO_BOOK_URL, headers=headers, params=params, timeout=5)
    res.raise_for_status()

    books = []
    for doc in res.json().get("documents", []):
        # isbn은 "ISBN10 ISBN13" 형태로 오기 때문에 마지막(13자리)을 사용
        isbn = doc["isbn"].split()[-1] if doc.get("isbn") else None
        if not isbn:
            continue
        books.append({
            "isbn": isbn,
            "title": doc["title"],
            "authors": ", ".join(doc.get("authors", [])),
            "publisher": doc.get("publisher", ""),
            "thumbnail": doc.get("thumbnail", ""),
        })
    return books