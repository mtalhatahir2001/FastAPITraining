from fastapi.testclient import TestClient
from project_3 import app
from starlette import status

client = TestClient(app=app)


def test_create_new_user():
    user = {
        "username": "test_t",
        "firstname": "Talha",
        "lastname": "Tahir",
        "password": "talha123",
        "p_number": "30396+++++",
    }
    response = client.post("/auth/register", data=user)
    assert response.status_code == status.HTTP_200_OK

    # if username or password is missing in request
    user = {
        "first_name": "Talha",
        "last_name": "Tahir",
        "p_number": "30396+++++",
    }
    response = client.post("/auth/register", data=user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login():
    user_creds = {
        "username": "t@code",
        "password": "talha123",
    }
    response = client.post("/auth/login", data=user_creds)
    assert response.status_code == status.HTTP_200_OK

    # if username is wrong
    user_creds = {
        "username": "tsaf@code",
        "password": "talha123",
    }
    response = client.post("/auth/login", data=user_creds)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # if password is wrong
    user_creds = {
        "username": "t@code",
        "password": "talha1234",
    }
    response = client.post("/auth/login", data=user_creds)
    assert response.status_code == status.HTTP_404_NOT_FOUND
