from database_config import engine
from fastapi import FastAPI
from models import Base

app = FastAPI()


Base.metadata.create_all(engine)


@app.get("/")
async def test_route():
    return {"greetings": "Db should be created by now."}
