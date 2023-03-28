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


@app.get("/books/{book_title}")
async def get_book_by_name(book_title: str):
    for i in BOOKS:
        if i.get("title").lower() == book_title.lower():
            return i
    return {"error": "book not found!"}


@app.get("/books/")
async def filter_books(category: str):
    filtered_list = list()
    for i in BOOKS:
        if i.get("category").lower() == category.lower():
            filtered_list.append(i)
    return filtered_list
