"""
This is the part of Section 15 assignment.\n
------------------------------------------
"""
import logging

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
logging.basicConfig(level=logging.DEBUG, filename="logs.txt")


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
    """
    Params
    ------
    user_id: int = user id
    db: Session = database object to query from.

    Will query the db to find the user with given user_id and reutrn its DB Model
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user == None:
        logging.error("no_user_in_db from get_single_user")
        raise HTTPException(status_code=404, detail="user_not_found")
    user.password = "***"
    result = UserModel(**user.__dict__)
    return result


@users_router.get("", status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: int = Query(gt=-1),
    db: local_session = Depends(get_sync_db),
) -> UserModel:
    """
    Takes user id as Query paramter and return the user info.
    """
    result = get_single_user(user_id, db)
    return result


@users_router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(
    user_id: int = Path(gt=-1),
    db: local_session = Depends(get_sync_db),
) -> UserModel:
    """
    Takes user id as Query paramter and return the user info.
    """
    result = get_single_user(user_id, db)
    return result


@users_router.get("/", status_code=status.HTTP_200_OK, response_model=None)
async def get_all_users(db: local_session = Depends(get_sync_db)) -> list[UserModel]:
    """
    Returns the list of all the users in a current db session.
    """
    users = db.query(User).all()
    return users


@users_router.put("/modify", status_code=status.HTTP_201_CREATED)
async def modify_current_user(
    user_info: PassInfo,
    user: dict = Depends(get_current_user),
    db: local_session = Depends(get_sync_db),
) -> dict[str, str]:
    """
    This will be used to change user password.\n
    will take old password and new password and will only change the password\n
    if old password matches the old password in db else will through 500.
    """
    if user == None:
        raise HTTPException(status_code=404, detail="user_not_found")
    else:
        user_in_db = db.query(User).filter(User.id == user.get("id")).first()
        if not verify_pass(user_info.old_password, user_in_db.password):
            logging.error(
                "old_pass not equal to current_pass -- from modify_current_user"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="old_pass_incorrect"
            )
        else:
            user_in_db.password = generate_hash(user_info.new_password)
            try:
                logging.info("updating user in db... -- from modify_current_user")
                db.add(user_in_db)
                db.commit()
            except Exception as e:
                logging.exception("Exception occured")
                raise HTTPException(status_code=500, detail="password_not_changed")
        return {"detail": "password_changed"}


@users_router.delete("/delete", status_code=status.HTTP_201_CREATED)
async def delete_current_user(
    user: dict = Depends(get_current_user), db: local_session = Depends(get_sync_db)
) -> dict[str, str]:
    """
    Takes no param. Will take the user Id form JWT Token passed in header.\n
    Will delete that user and all the todos assiciated with that user from the\n
    DB.
    """
    if user == None:
        logging.error("invalid_token -- from delete_current_user")
        raise HTTPException(status_code=404, detail="user_not_found")
    else:
        try:
            logging.info(f"deleting user{user.get('id')}.. -- from delete_current_user")
            db.query(Todo).filter(Todo.user_id == user.get("id")).delete()
            db.query(User).filter(User.id == user.get("id")).delete()
            db.commit()
        except Exception as e:
            logging.exception("Exception occured")
            raise HTTPException(status_code=500, detail="user_not_deleted")
        return {"detail": "user_deleted"}
