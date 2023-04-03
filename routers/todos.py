from database_config import local_session
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from models import Todo
from pydantic import BaseModel, Field
from sqlalchemy import and_
from starlette import status

from .auth import get_current_user, get_db

todo_router = APIRouter(
    prefix="/todos", tags=["Todos"], responses={401: {"user": "user_not_authenticated"}}
)

templates = Jinja2Templates(directory="templates")


class TodoModel(BaseModel):
    title: str = Field(min_length=0, max_length=32)
    discription: str = Field(min_length=0, max_length=100)
    priority: int = Field(gt=-1, lt=6)

    class Config:
        schema_extra = {
            "example": {
                "title": "Title of the todo",
                "discription": "Some detail about todo",
                "priority": 3,
            }
        }


@todo_router.get("/home_page", status_code=status.HTTP_200_OK)
async def get_home_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("edit-todo.html", {"request": request})


@todo_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_todos(
    db: local_session = Depends(get_db), user: dict = Depends(get_current_user)
) -> list:
    if user == None:
        raise HTTPException(status_code=404, detail="user_not_found")
    else:
        todos = db.query(Todo).filter(Todo.user_id == user.get("id")).all()
        return todos


@todo_router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo_by_id(
    todo_id: int = Path(gt=-1),
    user: dict = Depends(get_current_user),
    db: local_session = Depends(get_db),
) -> TodoModel:
    if user == None:
        raise HTTPException(status_code=404, detail="user_not_found")
    else:
        todo = (
            db.query(Todo)
            .filter(and_(Todo.user_id == user.get("id"), Todo.id == todo_id))
            .first()
        )
        if todo == None:
            raise HTTPException(status_code=404, detail="todo_not_found")
        result = TodoModel(**todo.__dict__)
        return result


@todo_router.post("/create_todo", status_code=status.HTTP_201_CREATED)
async def add_todo(
    todo: TodoModel,
    user: dict = Depends(get_current_user),
    db: local_session = Depends(get_db),
) -> dict[str, str]:
    if user == None:
        raise HTTPException(status_code=404, detail="user_not_found")
    new_todo = Todo(**todo.dict())
    new_todo.user_id = user.get("id")
    try:
        db.add(new_todo)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail="todo_not_inserted")
    return {"detail": "new_todo_created"}


@todo_router.put("/update_todo/{todo_id}", status_code=status.HTTP_201_CREATED)
async def update_todo(
    todo_id: int = Path(gt=-1),
    todo: TodoModel = None,
    user: dict = Depends(get_current_user),
    db: local_session = Depends(get_db),
) -> dict[str, str]:
    if user == None:
        raise HTTPException(status_code=404, detail="user_not_found")
    result = (
        db.query(Todo)
        .filter(and_(Todo.id == todo_id, Todo.user_id == user.get("id")))
        .first()
    )
    if result == None:
        raise HTTPException(status_code=404, detail="todo_not_found")
    else:
        result.title = todo.title
        result.discription = todo.discription
        result.priority = todo.priority
    try:
        db.add(result)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail="todo_not_inserted")
    return {"detail": "todo_updated"}


@todo_router.delete("/delete_todo/{todo_id}", status_code=status.HTTP_201_CREATED)
async def delete_todo(
    todo_id: int = Path(gt=-1),
    user: dict = Depends(get_current_user),
    db: local_session = Depends(get_db),
) -> dict[str, str]:
    if user == None:
        raise HTTPException(status_code=404, detail="user_not_found")
    db.query(Todo).filter(
        and_(Todo.id == todo_id, Todo.user_id == user.get("id"))
    ).delete()
    try:
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail="todo_not_deleted")
    return {"detail": "todo_deleted"}
