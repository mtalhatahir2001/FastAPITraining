"""
This is the part of Section 15 assignment.\n
------------------------------------------
"""

from database_config import local_session
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from models import Todo, User
from pydantic import BaseModel, Field
from starlette import status

from .auth import *

users_router = APIRouter(
    prefix="/users",
    tags=["Users (Assignment)"],
    responses={401: {"user": "user_not_authenticated"}},
)


class PassInfo(BaseModel):
    old_password: str = Field(min_length=0, max_length=8)
    new_password: str = Field(min_length=0, max_length=8)

    class Config:
        schema_extra = {
            "example": {
                "old_password": "old pass",
                "new_password": "new pass",
            }
        }


def get_single_user(user_id: int, db: local_session) -> UserModel:
    user = db.query(User).filter(User.id == user_id).first()
    if user == None:
        raise HTTPException(status_code=404, detail="user_not_found")
    user.password = "***"
    result = UserModel(**user.__dict__)
    return result


@users_router.get("", status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: int = Query(gt=-1),
    db: local_session = Depends(get_db),
) -> UserModel:
    result = get_single_user(user_id, db)
    return result


@users_router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: int = Path(gt=-1),
    db: local_session = Depends(get_db),
) -> UserModel:
    result = get_single_user(user_id, db)
    return result


@users_router.get("/", status_code=status.HTTP_200_OK)
async def get_all_users(db: local_session = Depends(get_db)) -> list:
    users = db.query(User).all()
    return users


@users_router.put("/modify", status_code=status.HTTP_201_CREATED)
async def modify_current_user(
    user_info: PassInfo,
    user: dict = Depends(get_current_user),
    db: local_session = Depends(get_db),
) -> dict[str, str]:
    if user == None:
        raise HTTPException(status_code=404, detail="user_not_found")
    else:
        user_in_db = db.query(User).filter(User.id == user.get("id")).first()
        if not verify_pass(user_info.old_password, user_in_db.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="old_pass_incorrect"
            )
        else:
            user_in_db.password = generate_hash(user_info.new_password)
            try:
                db.add(user_in_db)
                db.commit()
            except Exception as e:
                raise HTTPException(status_code=500, detail="password_not_changed")
        return {"detail": "password_changed"}


@users_router.delete("/delete", status_code=status.HTTP_201_CREATED)
async def delete_current_user(
    user: dict = Depends(get_current_user), db: local_session = Depends(get_db)
) -> dict[str, str]:
    if user == None:
        raise HTTPException(status_code=404, detail="user_not_found")
    else:
        try:
            db.query(Todo).filter(Todo.user_id == user.get("id")).delete()
            db.query(User).filter(User.id == user.get("id")).delete()
            db.commit()
        except Exception as e:
            raise HTTPException(status_code=500, detail="user_not_deleted")
        return {"detail": "user_deleted"}
