from fastapi import FastAPI

app = FastAPI()

BOOKS = [
    {"title": "Physics", "author": "Some random dude", "category": "science"},
    {"title": "Computer", "author": "Another random dude", "category": "Science"},
    {"title": "English", "author": "Some british guy", "category": "Literature"},
]


@app.get("/books")
async def get_books():
    return BOOKS
