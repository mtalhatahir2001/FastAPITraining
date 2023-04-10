import logging

from database_config import async_engine
from fastapi import FastAPI
from models import Base
from routers.auth import auth_router
from routers.todos import todo_router
from routers.users import users_router

app = FastAPI()


logging.basicConfig(level=logging.DEBUG, filename="logs.txt")
logging.info(f"initializing Db... --from {__name__}")


@app.on_event("startup")
async def init_tables():
    """
    Replacing Base.metadata.create_all() with the code below for the purpose of async table creation.\n
    Detail
    ------
    This startup event has nothing to do with the asyncio, it just calls the function on startup.\n
    However since aour engine is now async we need to create tables that way.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth_router)
app.include_router(todo_router)
app.include_router(users_router)
