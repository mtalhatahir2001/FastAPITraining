from fastapi import Body, FastAPI

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


@app.get("/books/filter/{author}")
async def filter_books(author: str):
    filtered_list = list()
    for i in BOOKS:
        if i.get("author").lower() == author.lower():
            filtered_list.append(i)
    return filtered_list


@app.post("/books/create_book")
async def add_new_books(new_book=Body()):
    BOOKS.append(new_book)
    return {"success": "Book added"}


@app.put("/books/update_book")
async def add_new_books(new_book=Body()):
    for index, i in enumerate(BOOKS):
        if i.get("title").lower() == new_book.get("title").lower():
            BOOKS[index] = new_book
            return {"success": "Book Updated"}
    return {"error": "No matching title found"}


@app.delete("/books/delete_book/{book_title}")
async def get_book_by_name(book_title: str):
    for index, i in enumerate(BOOKS):
        if i.get("title").lower() == book_title.lower():
            del BOOKS[index]
            return {"success": "Book Deleted"}
    return {"error": "No matching title found"}
