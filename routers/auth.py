import sys
from typing import Any, List

from database_config import local_session
from fastapi import APIRouter, Depends
from models import User
from passlib.context import CryptContext
from pydantic import BaseModel, Field

sys.path.append("..")


auth_router = APIRouter(
    prefix="/users", tags=["users"], responses={401: {"user": "Not Authenticated"}}
)


def get_db():
    try:
        db = local_session()
        yield db
    finally:
        db.close()


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_hash(password: str) -> str:
    return bcrypt_context.hash(password)


class UserModel(BaseModel):
    username: str = Field(min_length=0, max_length=10)
    first_name: str = Field(min_length=0, max_length=32)
    last_name: str = Field(min_length=0, max_length=32)
    password: str = Field(min_length=0, max_length=8)

    class Config:
        schema_extra = {
            "example": {
                "username": "A unique username",
                "first_name": "User's first name",
                "last_name": "User's last name",
                "password": "Password",
            }
        }


@auth_router.get("/", response_model=List[UserModel])
async def get_all_users(db: local_session = Depends(get_db)) -> List[UserModel]:
    users = db.query(User).all()
    return users


@auth_router.post("/create_new")
async def create_new_user(
    new_user: UserModel, db: local_session = Depends(get_db)
) -> dict:
    user = User(**new_user.dict())
    user.password = generate_hash(new_user.password)
    db.add(user)
    db.commit()
    return {"status": "user added."}
