import logging
from datetime import datetime, timedelta

from const import ERRORS
from database_config import local_session
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from models import User
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from starlette import status

auth_router = APIRouter(
    prefix="/auth", tags=["Auth"], responses={401: {"user": "user_not_authenticated"}}
)
logging.basicConfig(level=logging.DEBUG, filename="logs.txt")

templates = Jinja2Templates(directory="templates")


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


async def get_current_user(request: Request) -> dict[str, str] | None:
    """
    Will read the token through fastapi.Request and returns the payload.\n
    Will return None if JWTError is raised.
    """
    try:
        token = request.cookies.get("access_token")
        if token == None:
            raise JWTError
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=ALGO)
        user_id = payload.get("user_id")
        username = payload.get("username")
        return {"id": user_id, "username": username}
    except JWTError:
        logging.error(f"{ERRORS['invalid_token']} -- from {__name__}.get_current_user")
        return None


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


@auth_router.get("/login", status_code=status.HTTP_200_OK)
async def get_login_page(request: Request) -> HTMLResponse:
    """
    Displays the login page.
    """
    return templates.TemplateResponse("login.html", {"request": request})


@auth_router.get("/register", status_code=status.HTTP_200_OK)
async def get_register_page(request: Request) -> HTMLResponse:
    """
    Displays the Register page.
    """
    return templates.TemplateResponse("register.html", {"request": request})


@auth_router.post("/register", status_code=status.HTTP_303_SEE_OTHER)
async def get_register_page(
    request: Request,
    p_number: str = Form(...),
    username: str = Form(...),
    firstname: str = Form(...),
    lastname: str = Form(...),
    password: str = Form(...),
    db: local_session = Depends(get_db),
) -> RedirectResponse:
    """
    Reads the user data from Form object submited as post request.\n
    and inserts that to DB\n
    Response
    --------
    Redirect to auth/login
    """
    user = User(
        username=username,
        first_name=firstname,
        last_name=lastname,
        p_number=p_number,
        password=generate_hash(password),
    )
    try:
        logging.info(
            f"Adding user {user.username} to database -- from {__name__}.get_register_page"
        )
        db.add(user)
        db.commit()
    except Exception as e:
        logging.exception(f"Exception")
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": ERRORS["user_not_inserted"]}
        )
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_303_SEE_OTHER)


@auth_router.post("/login", status_code=status.HTTP_200_OK, response_model=None)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: local_session = Depends(get_db),
) -> RedirectResponse | HTMLResponse:
    """
    Read the form data into OAuth2PasswordRequestForm that\n
    expects the user to submit the form having username and password fields.\n
    Response
    --------
    Redirect to /todos/home with the access_token as cookie.
    """
    user = db.query(User).filter(User.username == form_data.username).first()
    if user == None:
        logging.error(f"{ERRORS['invalid_username']} -- from {__name__}.login")
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": ERRORS["invalid_username"]}
        )
    else:
        if verify_pass(form_data.password, user.password):
            token = generate_token(user.id, user.username)
            response = RedirectResponse(
                url="/todos/home", status_code=status.HTTP_303_SEE_OTHER
            )
            response.set_cookie(key="access_token", value=token, httponly=True)
            return response
        else:
            logging.error(f"{ERRORS['invalid_password']} -- from {__name__}.login")
            return templates.TemplateResponse(
                "login.html", {"request": request, "error": ERRORS["invalid_password"]}
            )
