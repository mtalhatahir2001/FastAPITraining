from fastapi.testclient import TestClient
from project_3 import app
from starlette import status

client = TestClient(app=app)


def test_get_all_todos():
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InRAY29kZSIsImV4cCI6MTY4MDc3MzAwOX0.TTjAmS6YPtbLvq_6639E107Hu9i0klVn4K2rgsyXk00"
    todo = {
        "id": 7,
        "title": "Complete proje 2",
        "discription": "chnaged db",
        "priority": 2,
        "user_id": 6,
    }
    response = client.get("/todos/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0] == todo


def test_get_todo_by_id():
    response = client.get("/todos/7")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InRAY29kZSIsImV4cCI6MTY4MDc3MzAwOX0.TTjAmS6YPtbLvq_6639E107Hu9i0klVn4K2rgsyXk00"
    todo = {
        "title": "Complete proje 2",
        "discription": "chnaged db",
        "priority": 2,
    }
    response = client.get("/todos/7", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == todo
    response = client.get("/todos/-1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    # Id doesn't exsist
    response = client.get("/todos/1000", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "todo_not_found"}


def test_add_todo():
    response = client.post("/todos/create_todo")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InRAY29kZSIsImV4cCI6MTY4MDc3MzAwOX0.TTjAmS6YPtbLvq_6639E107Hu9i0klVn4K2rgsyXk00"
    todo = {
        "title": "Complete proje 3",
        "discription": "chnaged db",
        "priority": 5,
    }
    response = client.post(
        "/todos/create_todo", headers={"Authorization": f"Bearer {token}"}, json=todo
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"detail": "new_todo_created"}


def test_update_todo():
    response = client.put("/todos/update_todo/8")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InRAY29kZSIsImV4cCI6MTY4MDc3MzAwOX0.TTjAmS6YPtbLvq_6639E107Hu9i0klVn4K2rgsyXk00"
    todo = {
        "title": "Complete proje 2",
        "discription": "chnaged db",
        "priority": 2,
    }
    response = client.put(
        "/todos/update_todo/8", headers={"Authorization": f"Bearer {token}"}, json=todo
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"detail": "todo_updated"}
    response = client.put(
        "/todos/update_todo/-1", headers={"Authorization": f"Bearer {token}"}, json=todo
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    # Id doesn't exsist
    response = client.put(
        "/todos/update_todo/1000",
        headers={"Authorization": f"Bearer {token}"},
        json=todo,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "todo_not_found"}


def test_delete_todo():
    response = client.delete("/todos/delete_todo/8")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}

    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InRAY29kZSIsImV4cCI6MTY4MDc3MzAwOX0.TTjAmS6YPtbLvq_6639E107Hu9i0klVn4K2rgsyXk00"
    response = client.delete(
        "/todos/delete_todo/8", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"detail": "todo_deleted"}
    response = client.delete(
        "/todos/delete_todo/-1", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
