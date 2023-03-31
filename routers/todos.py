from database_config import local_session
from fastapi import APIRouter, Depends, HTTPException
from models import Todo
from pydantic import BaseModel, Field
from starlette import status

from .auth import get_current_user, get_db

todo_router = APIRouter(
    prefix="/todos", tags=["Todos"], responses={401: {"user": "user_not_authenticated"}}
)


class TodoModel(BaseModel):
    title: str = Field(min_length=0, max_length=32)
    discription: str = Field(min_length=0, max_length=100)
    priority: int = Field(gt=-1, lt=6)


@todo_router.get("/")
async def get_all_todos(db: local_session = Depends(get_db)):
    return db.query(Todo).all()


@todo_router.post("/create_todo", status_code=status.HTTP_201_CREATED)
async def add_todo(
    todo: TodoModel,
    user: dict = Depends(get_current_user),
    db: local_session = Depends(get_db),
) -> dict:
    if user == None:
        raise HTTPException(status_code=404, detail="user_not_found")
    new_todo = Todo(**todo.dict())
    new_todo.user_id = user.get("id")
    try:
        db.add(new_todo)
        db.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="todo_not_inserted")
    return {"detail": "new_todo_created"}
