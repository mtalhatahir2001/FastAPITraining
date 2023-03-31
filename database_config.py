from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

CONNECTION_STRING = "postgresql://postgres:1234@localhost:5432/todo_app"

engine = create_engine(CONNECTION_STRING, echo=False)

local_session = sessionmaker(bind=engine)
