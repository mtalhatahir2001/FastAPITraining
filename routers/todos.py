import logging
from contextlib import asynccontextmanager

from const import ERRORS
from database_config import async_local_session
from fastapi import APIRouter, Form, HTTPException, Path, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models import Todo
from pydantic import BaseModel, Field
from sqlalchemy import and_, delete, select
from starlette import status

from .auth import get_current_user

todo_router = APIRouter(
    prefix="/todos", tags=["Todos"], responses={401: {"user": "user_not_authenticated"}}
)
logging.basicConfig(level=logging.DEBUG, filename="logs.txt")

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def get_async_db():
    """
    Calling this generator function will yield the DB object that can directly be used to query database.\n
    What this async context manager does is close the session when our code stops using it.\n
    """
    try:
        session = async_local_session
        async with session() as db:
            yield db
    except Exception as e:
        await db.rollback()
    finally:
        await db.close()


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
async def get_home_page(request: Request) -> RedirectResponse | HTMLResponse:
    """
    Verifys the user from access_token in cookies then return Home.html if token valid else\n
    redirect to login.
    """
    user = await get_current_user(request)
    if user == None:
        logging.error(f"{ERRORS['invalid_token']} -- from {__name__}.get_home_page")
        return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    async with get_async_db() as db:
        todos = await db.execute(select(Todo).where(Todo.user_id == user.get("id")))
        todos = todos.scalars().all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos})


@todo_router.get(
    "/edit_todo/{todo_id}", status_code=status.HTTP_200_OK, response_model=None
)
async def get_edit_todo_page(
    request: Request, todo_id: int = Path(gt=-1)
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
    # todo = (
    #     db.query(Todo)
    #     .filter(and_(Todo.user_id == user.get("id"), Todo.id == todo_id))
    #     .first()
    # )
    async with get_async_db() as db:
        todo = await db.execute(
            select(Todo).where(and_(Todo.user_id == user.get("id"), Todo.id == todo_id))
        )
        todo = todo.scalars().first()
    return templates.TemplateResponse(
        "edit-todo.html", {"request": request, "todo": todo}
    )


@todo_router.get("/add_todo", status_code=status.HTTP_200_OK, response_model=None)
async def get_add_todo_page(request: Request) -> RedirectResponse | HTMLResponse:
    """
    Verifys the user from access_token in cookies then return add-todo.html if token valid else\n
    redirect to login.
    """
    user = await get_current_user(request)
    if user == None:
        logging.error(f"{ERRORS['invalid_token']} -- from {__name__}.get_home_page")
        return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("add-todo.html", {"request": request})


@todo_router.post("/add_todo", status_code=status.HTTP_201_CREATED, response_model=None)
async def add_todo(
    request: Request,
    todo_title: str = Form(...),
    todo_description: str = Form(...),
    todo_priority: int = Form(...),
) -> RedirectResponse | HTMLResponse:
    """
    Requires the todo modal to be passed as post body as Form and adds it to the db for the current user.\n
    Requires the the token to be passed in cookie.
    """
    user = await get_current_user(request)
    if user == None:
        logging.error(f"{ERRORS['invalid_token']} -- from {__name__}.update_todo")
        return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    new_todo = Todo(
        title=todo_title, discription=todo_description, priority=todo_priority
    )
    new_todo.user_id = user.get("id")
    try:
        logging.info(f"Adding todo {new_todo.title} to db -- from {__name__}.add_todo")
        async with get_async_db() as db:
            db.add(new_todo)
            await db.commit()
    except Exception as e:
        logging.exception(f"Exception")
        return RedirectResponse("/todos/home", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse("/todos/home", status_code=status.HTTP_303_SEE_OTHER)


@todo_router.post(
    "/edit_todo/{todo_id}", status_code=status.HTTP_201_CREATED, response_model=None
)
async def update_todo(
    request: Request,
    todo_id: int = Path(gt=-1),
    todo_title: str = Form(...),
    todo_description: str = Form(...),
    todo_priority: int = Form(...),
) -> RedirectResponse | HTTPException:
    """
    Takes todo id as path param and updated todo as form body and updates the todo in the db with id passed as param.\n
    Requires the the token to be passed in as cookie.
    """
    user = await get_current_user(request)
    if user == None:
        logging.error(f"{ERRORS['invalid_token']} -- from {__name__}.update_todo")
        return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    async with get_async_db() as db:
        result = await db.execute(
            select(Todo).where(and_(Todo.id == todo_id, Todo.user_id == user.get("id")))
        )
        result = result.scalars().first()
    if result == None:
        logging.error(f"{ERRORS['invalid_todo']} -- from {__name__}.update_todo")
        return RedirectResponse("/todos/home", status_code=status.HTTP_303_SEE_OTHER)
    else:
        result.title = todo_title
        result.discription = todo_description
        result.priority = todo_priority
    try:
        logging.info(f"Updating todo {result.id} -- from {__name__}.update_todo")
        async with get_async_db() as db:
            db.add(result)
            await db.commit()
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
) -> RedirectResponse | HTMLResponse:
    """
    Takes todo id as path param deletes the todo in the db with id passed as param.\n
    Requires the the token to be passed in cookie.
    """
    user = await get_current_user(request)
    if user == None:
        logging.error(f"{ERRORS['invalid_token']} -- from {__name__}.delete_todo")
        return RedirectResponse("/auth/login", status_code=status.HTTP_303_SEE_OTHER)
    async with get_async_db() as db:
        result = await db.execute(
            delete(Todo).where(and_(Todo.id == todo_id, Todo.user_id == user.get("id")))
        )
        try:
            logging.info(f"Deleting todo {todo_id} -- from {__name__}.delete_todo")
            await db.commit()
        except Exception as e:
            logging.exception("Exception")
            return RedirectResponse(
                "/todos/home", status_code=status.HTTP_303_SEE_OTHER
            )
    return RedirectResponse("/todos/home", status_code=status.HTTP_303_SEE_OTHER)
