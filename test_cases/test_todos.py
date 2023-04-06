from fastapi.testclient import TestClient
from project_3 import app
from starlette import status

client = TestClient(app=app)


def test_get_all_todos():
    response = client.get("/todos/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}
