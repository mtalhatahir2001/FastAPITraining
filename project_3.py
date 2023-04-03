import logging

from database_config import engine
from fastapi import FastAPI
from models import Base
from routers.auth import auth_router
from routers.todos import todo_router
from routers.users import users_router

app = FastAPI()


logging.basicConfig(level=logging.DEBUG, filename="logs.txt")
logging.info(f"initializing Db... --from {__name__}")
Base.metadata.create_all(engine)


app.include_router(auth_router)
app.include_router(todo_router)
app.include_router(users_router)
