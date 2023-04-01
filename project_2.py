from typing import Optional

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field
from starlette import status

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


@app.get("/books", status_code=status.HTTP_200_OK)
async def get_all_books() -> list:
    return BOOKS


@app.post("/books/create_book", status_code=status.HTTP_201_CREATED)
async def get_all_books(book_request: BookRequest) -> dict:
    book = Book(**book_request.dict())
    book.id = 1 if len(BOOKS) == 0 else BOOKS[len(BOOKS) - 1].id + 1
    BOOKS.append(book)
    return {"detail": "new_book_created"}


# Similarly we can also write put and delete methods
@app.get("/books/", status_code=status.HTTP_200_OK)
async def get_books_by_rating(rating: float = Query(gt=0, lt=6)) -> list:
    result_books = list()
    for i in BOOKS:
        if i.rating == rating:
            result_books.append(i)
    if len(result_books) == 0:
        raise HTTPException(status_code=404, detail="No record found")
    else:
        return result_books


# Assigment question to filter books by publish_date
@app.get("/books/{publish_date}", status_code=status.HTTP_200_OK)
async def get_books_by_rating(publish_date: float = Path(gt=1899, lt=3000)) -> list:
    result_books = list()
    for i in BOOKS:
        if i.publish_date == publish_date:
            result_books.append(i)
    if len(result_books) == 0:
        raise HTTPException(status_code=404, detail="No record found")
    else:
        return result_books
