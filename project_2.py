from fastapi import FastAPI

app = FastAPI()


class Book:
    def __init__(
        self, id: int, title: str, author: str, description: str, rating: float
    ):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating


BOOKS = [
    Book(1, "Physic", "Talha", "Applied Physics", 4),
    Book(2, "Chemistry", "Tahir", "Organic chemistry", 4.5),
    Book(3, "Computer", "Talha", "Data Structures", 5),
]


@app.get("/books")
def get_all_books():
    return BOOKS
