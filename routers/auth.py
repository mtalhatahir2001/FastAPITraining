import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from database_config import async_local_session, local_session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models import User
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy import select
from starlette import status

auth_router = APIRouter(
    prefix="/auth", tags=["Auth"], responses={401: {"user": "user_not_authenticated"}}
)
logging.basicConfig(level=logging.DEBUG, filename="logs.txt")


@asynccontextmanager
async def get_db():
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


def get_sync_db():
    """
    Calling this generator function will yield the DB object that can directly be used to query database.\n
    """
    try:
        db = local_session()
        yield db
    except Exception as e:
        db.rollback()
    finally:
        db.close()


# CryptContext the object of the scheme passed i.e bcrypt that can be used
# to hash passward before add them to db
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="/login")

SECRET_KEY = "my_super_secret_key"
ALGO = "HS256"


def generate_hash(password: str) -> str:
    """
    Will use the bcrypt to return the hashed version of the string passed.\n
    Param
    ------
    password: str = string to hash
    """
    return bcrypt_context.hash(password)


def verify_pass(password: str, hash_pass: str) -> bool:
    """
    Will use the bcrypt to verify if hashed version matches the string passed.\n
    Param
    ------
    password: str = orginal string
    hash_pass: str = hash password to match with
    """
    return bcrypt_context.verify(password, hash_pass)


def generate_token(user_id: int, username: str) -> str:
    """
    Returns the JWT token with params added as payload and expire time of 30 mins\n
    Params
    --------
    user_id: int
    username: str
    """
    expire_time = datetime.now() + timedelta(minutes=30)
    token = jwt.encode(
        {"user_id": user_id, "username": username, "exp": expire_time},
        SECRET_KEY,
        algorithm=ALGO,
    )
    return token


async def get_current_user(token: str = Depends(oauth_bearer)) -> dict[str, str]:
    """
    Read the token through dependency injection and returns the payload.\n
    Will raise 401 if JWT Token is not verified.
    """
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGO)
        user_id = payload.get("user_id")
        username = payload.get("username")
        return {"id": user_id, "username": username}
    except JWTError as e:
        logging.error(f"invalid_token -- from {__name__}.get_current_user")
        raise HTTPException(status_code=401, detail="unauthorized_user")


class UserModel(BaseModel):
    username: str = Field(min_length=0, max_length=10)
    first_name: str = Field(min_length=0, max_length=32)
    last_name: str = Field(min_length=0, max_length=32)
    password: str = Field(min_length=0, max_length=8)
    p_number: str = Field(min_length=0, max_length=11)

    class Config:
        schema_extra = {
            "example": {
                "username": "A unique username",
                "first_name": "User's first name",
                "last_name": "User's last name",
                "password": "Password",
                "p_number": "Phone num",
            }
        }


@auth_router.post("/create_new", status_code=status.HTTP_201_CREATED)
async def create_new_user(new_user: UserModel) -> dict[str, str]:
    """
    Reads the user json object passed as pydantic object.\n
    and inserts that to DB
    """
    user = User(**new_user.dict())
    user.password = generate_hash(new_user.password)
    try:
        logging.info(
            f"adding user{user.username} to db -- from {__name__}.create_new_user"
        )
        async with get_db() as db:
            db.add(user)
            await db.commit()
    except Exception as e:
        logging.exception(f"Exception")
        raise HTTPException(status_code=500, detail="user_not_inserted")
    return {"detail": "new_user_created"}


async def verify_user_async(password: str, user: UserModel) -> dict[str, str]:
    """
    This function is an async version of verify_password + generate_token.
    Returns
    -------
    JWT token
    """
    if user == None:
        logging.error(f"invalid_user -- from {__name__}.login")
        raise HTTPException(status_code=404, detail="user_not_found")
    else:
        if verify_pass(password, user.password):
            token = generate_token(user.id, user.username)
            return {"access_token": token}
        else:
            logging.error(f"invlid_password -- from {__name__}.login")
            raise HTTPException(404, detail="invalid_password")


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str] | None:
    """
    Read the form data into OAuth2PasswordRequestForm that\n
    expects the user to submit the form having username and password fields.\n
    returns the token if login creds match else raise 401
    """
    async with get_db() as db:
        try:
            user = await db.execute(
                select(User).where(User.username == form_data.username)
            )
            token = await verify_user_async(form_data.password, user.scalars().first())
        except Exception as e:
            logging.exception("Exception")
        return token
