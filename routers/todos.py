import logging

from const import ERRORS
from database_config import local_session
from fastapi import APIRouter, Depends, Form, HTTPException, Path, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models import Todo
from pydantic import BaseModel, Field
from sqlalchemy import and_
from starlette import status

from .auth import get_current_user, get_db

todo_router = APIRouter(
    prefix="/todos", tags=["Todos"], responses={401: {"user": "user_not_authenticated"}}
)
logging.basicConfig(level=logging.DEBUG, filename="logs.txt")

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


@todo_router.get("/home", status_code=status.HTTP_200_OK, response_model=None)
async def get_home_page(
    request: Request, db: local_session = Depends(get_db)
) -> RedirectResponse | HTMLResponse:
    """
    Verifys the user from access_token in cookies then return Home.html if token valid else\n
    redirect to login.
    """
    user = await get_current_user(request)
    todos = db.query(Todo).filter(Todo.user_id == user.get("id")).all()
    if user == None:
        logging.error(f"{ERRORS['invalid_token']} -- from {__name__}.get_home_page")
        return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})


@todo_router.get(
    "/edit_todo/{todo_id}", status_code=status.HTTP_200_OK, response_model=None
)
async def get_edit_todo_page(
    request: Request, todo_id: int = Path(gt=-1), db: local_session = Depends(get_db)
) -> HTMLResponse | RedirectResponse:
    """
    Verifys the user from access_token in cookies then return edit.html if token valid else\n
    redirect to login.
    """
    user = await get_current_user(request)
    if user == None:
        logging.error(
            f"{ERRORS['invalid_token']} -- from {__name__}.get_edit_todo_page"
        )
        return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    todo = (
        db.query(Todo)
        .filter(and_(Todo.user_id == user.get("id"), Todo.id == todo_id))
        .first()
    )
    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": todo}
    )


@todo_router.get("/add_todo", status_code=status.HTTP_200_OK)
async def get_add_todo_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("add-todo.html", {"request": request})


# @todo_router.post("/create_todo", status_code=status.HTTP_201_CREATED)
# async def add_todo(
#     todo: TodoModel,
#     user: dict = Depends(get_current_user),
#     db: local_session = Depends(get_db),
# ) -> dict[str, str]:
#     """
#     Requires the todo modal to be passed as post body as json and adds it to the db for the current user.\n
#     Requires the the token to be passed in header.
#     """
#     if user == None:
#         logging.error(f"invalid_token -- from {__name__}.add_todo")
#         raise HTTPException(status_code=404, detail="user_not_found")
#     new_todo = Todo(**todo.dict())
#     new_todo.user_id = user.get("id")
#     try:
#         logging.info(
#             f"adding todo{new_todo.title} to db -- from {__name__}.get_todo_by_id"
#         )
#         db.add(new_todo)
#         db.commit()
#     except Exception as e:
#         logging.exception(f"Exception")
#         raise HTTPException(status_code=500, detail="todo_not_inserted")
#     return {"detail": "new_todo_created"}


@todo_router.post(
    "/edit_todo/{todo_id}", status_code=status.HTTP_201_CREATED, response_model=None
)
async def update_todo(
    request: Request,
    todo_id: int = Path(gt=-1),
    todo_title: str = Form(...),
    todo_description: str = Form(...),
    todo_priority: int = Form(...),
    db: local_session = Depends(get_db),
) -> RedirectResponse | HTTPException:
    """
    Takes todo id as path param and updated todo as form body and updates the todo in the db with id passed as param.\n
    Requires the the token to be passed in as cookie.
    """
    user = await get_current_user(request)
    if user == None:
        logging.error(f"{ERRORS['invalid_token']} -- from {__name__}.update_todo")
        return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    result = (
        db.query(Todo)
        .filter(and_(Todo.id == todo_id, Todo.user_id == user.get("id")))
        .first()
    )
    if result == None:
        logging.error(f"{ERRORS['invalid_todo']} -- from {__name__}.update_todo")
        return RedirectResponse("/todos/home", status_code=status.HTTP_303_SEE_OTHER)
    else:
        result.title = todo_title
        result.discription = todo_description
        result.priority = todo_priority
    try:
        logging.info(f"Updating todo {result.id} -- from {__name__}.update_todo")
        db.add(result)
        db.commit()
    except Exception as e:
        logging.exception(f"Exceptions")
        return RedirectResponse("/todos/home", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse("/todos/home", status_code=status.HTTP_303_SEE_OTHER)


@todo_router.get(
    "/delete_todo/{todo_id}", status_code=status.HTTP_201_CREATED, response_model=None
)
async def delete_todo(
    request: Request,
    todo_id: int = Path(gt=-1),
    db: local_session = Depends(get_db),
) -> RedirectResponse | HTMLResponse:
    """
    Takes todo id as path param deletes the todo in the db with id passed as param.\n
    Requires the the token to be passed in cookie.
    """
    user = await get_current_user(request)
    if user == None:
        logging.error(f"{ERRORS['invalid_token']} -- from {__name__}.delete_todo")
        return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    db.query(Todo).filter(
        and_(Todo.id == todo_id, Todo.user_id == user.get("id"))
    ).delete()
    try:
        logging.info(f"Deleting todo {todo_id} -- from {__name__}.delete_todo")
        db.commit()
    except Exception as e:
        logging.exception("Exception")
        return RedirectResponse("/todos/home", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse("/todos/home", status_code=status.HTTP_303_SEE_OTHER)
