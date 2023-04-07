from fastapi.testclient import TestClient
from project_3 import app
from starlette import status

client = TestClient(app=app)


def test_get_home_page():
    token = "access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InRAY29kZSIsImV4cCI6MTY4MDc5MTEyOX0.95biE5Q3oTBgfyJ8K7O6A10o8f0WTKB2xRm2sDws6p0"
    response = client.get("/todos/home", headers={"Cookie": token})
    assert response.status_code == status.HTTP_200_OK


def test_add_todo():
    # If user tries to add todo with out logging in (no cookie)
    todo = {
        "todo_title": "Test_add_to",
        "todo_description": "todo from test_todo.py",
        "todo_priority": 4,
    }
    response = client.post("/todos/add_todo", data=todo)
    # 200 since it will redirect to login.html
    assert response.status_code == status.HTTP_200_OK

    token = "access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3LCJ1c2VybmFtZSI6InRAY29kZSIsImV4cCI6MTY4MDg2NzU0NH0.CPoSBK9UG33TcWHOGXssotC5wDtzuQI0uwFpodXBhLY"
    response = client.post("/todos/add_todo", headers={"Cookie": token}, data=todo)
    assert response.status_code == status.HTTP_201_CREATED


def test_update_todo():
    todo = {
        "todo_title": "Test_add_to",
        "todo_description": "todo from test_todo.py",
        "todo_priority": 4,
    }
    # If user tries to add todo with out logging in (no cookie)
    response = client.post("/todos/edit_todo/1", data=todo)
    # 200 since it will redirect to login.html
    assert response.status_code == status.HTTP_200_OK

    token = "access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3LCJ1c2VybmFtZSI6InRAY29kZSIsImV4cCI6MTY4MDg2NzU0NH0.CPoSBK9UG33TcWHOGXssotC5wDtzuQI0uwFpodXBhLY"
    response = client.post("/todos/edit_todo/1", headers={"Cookie": token}, data=todo)
    assert response.status_code == status.HTTP_201_CREATED


def test_delete_todo():
    # If user tries to add todo with out logging in (no cookie)
    response = client.get("/todos/delete_todo/1")
    # 200 since it will redirect to login.html
    assert response.status_code == status.HTTP_200_OK

    token = "access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo3LCJ1c2VybmFtZSI6InRAY29kZSIsImV4cCI6MTY4MDg2NzU0NH0.CPoSBK9UG33TcWHOGXssotC5wDtzuQI0uwFpodXBhLY"
    response = client.get("/todos/delete_todo/1", headers={"Cookie": token})
    assert response.status_code == status.HTTP_201_CREATED
