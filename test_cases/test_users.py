from fastapi.testclient import TestClient
from project_3 import app
from starlette import status

client = TestClient(app=app)

"""
You will notice these test cases are for the api. Since\n
the actual routes in api are still api routes i.e they\n
return json instead of html
"""


def test_get_user_by_id():
    response = client.get("/users?user_id=6")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "username": "t@code",
        "first_name": "M Talha",
        "last_name": "Tahir",
        "password": "***",
        "p_number": "03096442471",
    }
    response = client.get("/users?user_id=-1")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_modify_current_user():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InRAY29kZSIsImV4cCI6MTY4MDc5MTEyOX0.95biE5Q3oTBgfyJ8K7O6A10o8f0WTKB2xRm2sDws6p0"
    response = client.put("/users/modify")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}

    # if old_pass didn't match to new pass
    pass_info = {"old_password": "talha124", "new_password": "talha124"}
    response = client.put(
        "/users/modify", json=pass_info, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # if success
    pass_info = {"old_password": "talha123", "new_password": "talha124"}
    response = client.put(
        "/users/modify", json=pass_info, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED


def test_delete_current_user():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjo2LCJ1c2VybmFtZSI6InRAY29kZSIsImV4cCI6MTY4MDc5MTEyOX0.95biE5Q3oTBgfyJ8K7O6A10o8f0WTKB2xRm2sDws6p0"
    response = client.delete("/users/delete")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}
    response = client.delete(
        "/users/delete", headers={"Authorization": f"Bearer {token}"}
    )
