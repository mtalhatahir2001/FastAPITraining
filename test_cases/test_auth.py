from fastapi.testclient import TestClient
from project_3 import app
from starlette import status

client = TestClient(app=app)


def test_create_new_user():
    user = {
        "username": "test_t",
        "first_name": "Talha",
        "last_name": "Tahir",
        "password": "talha123",
        "p_number": "30396+++++",
    }
    response = client.post("/auth/create_new", json=user)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"detail": "new_user_created"}

    # if username or password is missing in request
    user = {
        "first_name": "Talha",
        "last_name": "Tahir",
        "p_number": "30396+++++",
    }
    response = client.post("/auth/create_new", json=user)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login():
    user_creds = {
        "username": "t@code",
        "password": "talha123",
    }
    response = client.post("/auth/login", data=user_creds)
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("access_token") != None

    # if username is wrong
    user_creds = {
        "username": "tsaf@code",
        "password": "talha123",
    }
    response = client.post("/auth/login", data=user_creds)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("access_token") == None

    # if password is wrong
    user_creds = {
        "username": "t@code",
        "password": "talha1234",
    }
    response = client.post("/auth/login", data=user_creds)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json().get("access_token") == None
