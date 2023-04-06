import logging
from datetime import datetime, timedelta

from database_config import local_session
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models import User
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from starlette import status

auth_router = APIRouter(
    prefix="/auth", tags=["Auth"], responses={401: {"user": "user_not_authenticated"}}
)
logging.basicConfig(level=logging.DEBUG, filename="logs.txt")


def get_db():
    """
    Calling this generator function will yield the DB object that can directly be used to query database.
    """
    try:
        db = local_session()
        yield db
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
    except JWTError:
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
async def create_new_user(
    new_user: UserModel, db: local_session = Depends(get_db)
) -> dict[str, str]:
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
        db.add(user)
        db.commit()
    except Exception as e:
        logging.exception(f"Exception")
        raise HTTPException(status_code=500, detail="user_not_inserted")
    return {"detail": "new_user_created"}


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: local_session = Depends(get_db),
) -> dict[str, str]:
    """
    Read the form data into OAuth2PasswordRequestForm that\n
    expects the user to submit the form having username and password fields.\n
    returns the token if login creds match else raise 401
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if user == None:
        logging.error(f"invalid_user -- from {__name__}.login")
        raise HTTPException(status_code=404, detail="user_not_found")
    else:
        if verify_pass(form_data.password, user.password):
            token = generate_token(user.id, user.username)
            return {"access_token": token}
        else:
            logging.error(f"invlid_password -- from {__name__}.login")
            raise HTTPException(404, detail="invalid_password")
