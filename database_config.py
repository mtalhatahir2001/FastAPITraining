from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

CONNECTION_STRING = "postgresql+asyncpg://postgres:1234@localhost:5432/todo_app"


async_engine = create_async_engine(CONNECTION_STRING, echo=False, future=True)
async_local_session = sessionmaker(bind=async_engine, class_=AsyncSession)

sync_engine = create_engine(CONNECTION_STRING, echo=False)
local_session = sessionmaker(bind=sync_engine)
