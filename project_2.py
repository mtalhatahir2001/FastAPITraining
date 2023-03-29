from typing import Optional

from fastapi import FastAPI, Path
from pydantic import BaseModel, Field

app = FastAPI()


class Book:
    def __init__(
        self,
        id: int,
        title: str,
        author: str,
        description: str,
        rating: float,
        publish_date: int,
    ):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.publish_date = publish_date


class BookRequest(BaseModel):
    id: Optional[int]
    title: str = Field(min_length=3)
    author: str = Field(min_length=1)
    description: str = Field(max_length=100, min_length=1)
    rating: float = Field(gt=0, lt=6)
    publish_date: int = Field(gt=1899, lt=3000)

    class Config:
        schema_extra = {
            "example": {
                "title": "title of the book",
                "author": "person who wrote the book",
                "description": "one liners about the book",
                "rating": 4,
                "publish_date": 2012,
            }
        }


BOOKS = [
    Book(1, "Physic", "Talha", "Applied Physics", 4, 2014),
    Book(2, "Chemistry", "Tahir", "Organic chemistry", 4.5, 2014),
    Book(3, "Computer", "Talha", "Data Structures", 5, 2014),
]


@app.get("/books")
async def get_all_books():
    return BOOKS


@app.post("/books/create_book")
async def get_all_books(book_request: BookRequest):
    book = Book(**book_request.dict())
    book.id = 1 if len(BOOKS) == 0 else BOOKS[len(BOOKS) - 1].id + 1
    BOOKS.append(book)


# Similarly we can also write put and delete methods
@app.get("/books/")
async def get_books_by_rating(rating: float):
    result_books = list()
    for i in BOOKS:
        if i.rating == rating:
            result_books.append(i)
    return result_books


# Assigment question to filter books by publish_date
@app.get("/books/{publish_date}")
async def get_books_by_rating(publish_date: float = Path(gt=1899, lt=3000)):
    result_books = list()
    for i in BOOKS:
        if i.publish_date == publish_date:
            result_books.append(i)
    return result_books
