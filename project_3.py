from database_config import engine
from fastapi import FastAPI
from models import Base
from routers.auth import auth_router

app = FastAPI()


Base.metadata.create_all(engine)


app.include_router(auth_router)
