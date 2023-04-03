from fastapi import Body, FastAPI

app = FastAPI()

BOOKS = [
    {"title": "Physics", "author": "Some random dude", "category": "science"},
    {"title": "Computer", "author": "Another random dude", "category": "Science"},
    {"title": "English", "author": "Some british guy", "category": "Literature"},
]


@app.get("/books")
async def get_books() -> list[dict[str, str]]:
    """
    Will return list of books that are represented by dict \n
    Structure of Book
    ----------------
    keys = title, author and category
    """
    return BOOKS


@app.get("/books/{book_title}")
async def get_book_by_name(book_title: str) -> dict[str, str]:
    """
    Takes the title of the book as path param and returns a single book\n
    if not found throws an error.\n
    Params
    ------
    book_title: str = title of the book
    """
    for i in BOOKS:
        if i.get("title").lower() == book_title.lower():
            return i
    return {"error": "book not found!"}


@app.get("/books/")
async def filter_books(category: str) -> list[dict[str, str]]:
    """
    Will return the filterd list of books based on query param provided.\n
    Param
    ------
    ?cateogry: str = category of the book
    """
    filtered_list = list()
    for i in BOOKS:
        if i.get("category").lower() == category.lower():
            filtered_list.append(i)
    return filtered_list


@app.get("/books/filter/{author}")
async def filter_books(author: str) -> list[dict[str, str]]:
    """
    Will return the filterd list of books based on path param provided.\n
    Param
    ------
    author: str = author of the book
    """
    filtered_list = list()
    for i in BOOKS:
        if i.get("author").lower() == author.lower():
            filtered_list.append(i)
    return filtered_list


@app.post("/books/create_book")
async def add_new_books(new_book=Body()) -> dict[str, str]:
    """
    Accepts the json as post body and adds it to the books list.\n
    Body format
    -----------
    {"title": "Physics", "author": "Some random dude", "category": "science"},
    """
    BOOKS.append(new_book)
    return {"success": "Book added"}


@app.put("/books/update_book")
async def add_new_books(new_book=Body()) -> dict[str, str]:
    """
    Takes the book json as body and updates list where the title matches\n
    Body format
    -----------
    {"title": "Physics", "author": "Some random dude", "category": "science"},
    """
    for index, i in enumerate(BOOKS):
        if i.get("title").lower() == new_book.get("title").lower():
            BOOKS[index] = new_book
            return {"success": "Book Updated"}
    return {"error": "No matching title found"}


@app.delete("/books/delete_book/{book_title}")
async def get_book_by_name(book_title: str) -> dict[str, str]:
    """
    Takes the title of the book as path param and deletes the matching book\n
    if not found throws an error.\n
    Params
    ------
    book_title: str = title of the book
    """
    for index, i in enumerate(BOOKS):
        if i.get("title").lower() == book_title.lower():
            del BOOKS[index]
            return {"success": "Book Deleted"}
    return {"error": "No matching title found"}
