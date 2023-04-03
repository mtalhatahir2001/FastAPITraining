import logging

from database_config import local_session
from fastapi import APIRouter, Depends, HTTPException, Path
from models import Todo
from pydantic import BaseModel, Field
from sqlalchemy import and_
from starlette import status

from .auth import get_current_user, get_db

todo_router = APIRouter(
    prefix="/todos", tags=["Todos"], responses={401: {"user": "user_not_authenticated"}}
)
logging.basicConfig(level=logging.DEBUG, filename="logs.txt")


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


@todo_router.get("/", status_code=status.HTTP_200_OK, response_model=None)
async def get_all_todos(
    db: local_session = Depends(get_db), user: dict = Depends(get_current_user)
) -> list[Todo]:
    """
    Querys the Db and returns all the available todos for the current logged in user\n
    Requires the the token to be passed in header.
    """
    if user == None:
        logging.error(f"invalid_token -- from {__name__}.get_all_todos")
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
    """
    Querys the Db and returns all the available todos having id passed as path param for the current logged in user\n
    Requires the the token to be passed in header.
    """
    if user == None:
        logging.error(f"invalid_token -- from {__name__}.get_todo_by_id")
        raise HTTPException(status_code=404, detail="user_not_found")
    else:
        todo = (
            db.query(Todo)
            .filter(and_(Todo.user_id == user.get("id"), Todo.id == todo_id))
            .first()
        )
        if todo == None:
            logging.error(f"invalid_todo_id -- from {__name__}.get_todo_by_id")
            raise HTTPException(status_code=404, detail="todo_not_found")
        result = TodoModel(**todo.__dict__)
        return result


@todo_router.post("/create_todo", status_code=status.HTTP_201_CREATED)
async def add_todo(
    todo: TodoModel,
    user: dict = Depends(get_current_user),
    db: local_session = Depends(get_db),
) -> dict[str, str]:
    """
    Requires the todo modal to be passed as post body as json and adds it to the db for the current user.\n
    Requires the the token to be passed in header.
    """
    if user == None:
        logging.error(f"invalid_token -- from {__name__}.add_todo")
        raise HTTPException(status_code=404, detail="user_not_found")
    new_todo = Todo(**todo.dict())
    new_todo.user_id = user.get("id")
    try:
        logging.info(
            f"adding todo{new_todo.title} to db -- from {__name__}.get_todo_by_id"
        )
        db.add(new_todo)
        db.commit()
    except Exception as e:
        logging.exception(f"Exception")
        raise HTTPException(status_code=500, detail="todo_not_inserted")
    return {"detail": "new_todo_created"}


@todo_router.put("/update_todo/{todo_id}", status_code=status.HTTP_201_CREATED)
async def update_todo(
    todo_id: int = Path(gt=-1),
    todo: TodoModel = None,
    user: dict = Depends(get_current_user),
    db: local_session = Depends(get_db),
) -> dict[str, str]:
    """
    Takes todo id as path param and Todo json as body and updates the todo in the db with id passed as param.\n
    Requires the the token to be passed in header.
    """
    if user == None:
        logging.error(f"invalid_token -- from {__name__}.update_todo")
        raise HTTPException(status_code=404, detail="user_not_found")
    result = (
        db.query(Todo)
        .filter(and_(Todo.id == todo_id, Todo.user_id == user.get("id")))
        .first()
    )
    if result == None:
        logging.error(f"invalid_todo -- from {__name__}.update_todo")
        raise HTTPException(status_code=404, detail="todo_not_found")
    else:
        result.title = todo.title
        result.discription = todo.discription
        result.priority = todo.priority
    try:
        logging.info(f"updating todo{result.id} -- from {__name__}.update_todo")
        db.add(result)
        db.commit()
    except Exception as e:
        logging.exception(f"Exceptions")
        raise HTTPException(status_code=500, detail="todo_not_inserted")
    return {"detail": "todo_updated"}


@todo_router.delete("/delete_todo/{todo_id}", status_code=status.HTTP_201_CREATED)
async def delete_todo(
    todo_id: int = Path(gt=-1),
    user: dict = Depends(get_current_user),
    db: local_session = Depends(get_db),
) -> dict[str, str]:
    """
    Takes todo id as path param deletes the todo in the db with id passed as param.\n
    Requires the the token to be passed in header.
    """
    if user == None:
        logging.error(f"invalid_token -- from {__name__}.delete_todo")
        raise HTTPException(status_code=404, detail="user_not_found")
    db.query(Todo).filter(
        and_(Todo.id == todo_id, Todo.user_id == user.get("id"))
    ).delete()
    try:
        logging.info(f"deleting todo{todo_id} -- from {__name__}.delete_todo")
        db.commit()
    except Exception as e:
        logging.exception("Exception")
        raise HTTPException(status_code=500, detail="todo_not_deleted")
    return {"detail": "todo_deleted"}
