from fastapi.testclient import TestClient
from passlib.context import CryptContext
from . import main # app, ADMIN_PASSWORD, ADMIN_USERNAME, get_db 
import pytest
import os

from . import crud

ADMIN_USERNAME=os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD=os.getenv("ADMIN_PASSWORD")

@pytest.fixture(autouse=True)
def create_admin_user():
    with TestClient(main.app) as client:
        db = next(main.get_db())
        admin_user = main.schemas.UserCreate(username=main.ADMIN_USERNAME, email="admin@localhost.com", password=main.ADMIN_PASSWORD)
        db_admin = crud.create_user_admin(db, user=admin_user)
        db.add(db_admin)
        db.commit()
        yield db_admin

@pytest.fixture()
def client():
    with TestClient(main.app) as client:
        yield client

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_access_token(client: TestClient):
    in_data: dict = {
        "username": "accname",
        "email": "acc@mail.com",
        "password": "123"
    }
    client.post("/student/create/", json=in_data)
    response = client.post("/login/", data={"username": "accname", "password": "123"})
    return response.json()["access_token"]

def admin_get_access_token(client: TestClient):
    in_data: dict = {
        "username": main.ADMIN_USERNAME,
        "password": main.ADMIN_PASSWORD
    }
    response = client.post("/login/", data=in_data)
    return response.json()["access_token"]

def test_create_profile_student_success(client: TestClient):
    in_data: dict = {
        "username": "test_name",
        "email": "test@email.com",
        "password": "12345"
    }
    response = client.post("/student/create/", json=in_data)
    assert response.status_code == 201
    assert response.json()["username"] == "test_name"
    assert response.json()["email"] == "test@email.com"
    assert response.json()["user_type"] == "STU"
    assert response.json()["is_active"] == True

def test_create_profile_student_bad_user_name(client: TestClient):
    in_data: dict = {
        "username": "test1_name",
        "email": "test1@email.com",
        "password": "12345",
    }
    in_data2: dict = {
        "username": "test1_name",
        "email": "test12@email.com",
        "password": "12345",
    }
    client.post("/student/create/", json=in_data)
    response = client.post("/student/create/", json=in_data2)
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}

def test_create_profile_student_bad_email(client: TestClient):
    in_data: dict = {
        "username": "test2_name",
        "email": "test2@email.com",
        "password": "12345",
    }
    in_data2: dict = {
        "username": "test_name2",
        "email": "test2@email.com",
        "password": "12345",
    }
    client.post("/student/create/", json=in_data)
    response = client.post("student/create/", json=in_data2)
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

def test_create_profile_student_invalid_email(client: TestClient):
    in_data: dict = {
        "username": "testname",
        "email": "testemail.com",
        "password": "12345"
    }
    response = client.post("/student/create/", json=in_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email"}

def test_login_success(client: TestClient):
    in_data: dict = {
        "username": "test3_name",
        "email": "test3@email.com",
        "password": "12345",
    }
    client.post("/student/create/", json=in_data)

    response = client.post("/login/", data={
        "username": "test3_name",
        "password": "12345"
    })

    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()

def test_login_non_existant_user(client: TestClient):
    in_data: dict = {
        "username": "wrong_name",
        "password": "12345"
    }
    response = client.post("/login/", data=in_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_login_wrong_password_for_user(client: TestClient):
    in_data: dict = {
        "username": "test5_name",
        "email": "test5@email.com",
        "password": "12345",
    }
    in_data2: dict = {
        "username": "test5_name",
        "password": "123456"
    }
    client.post("/student/create/", json=in_data)
    response = client.post("/login/", data=in_data2)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_get_assignments_success(client: TestClient):
    token = get_access_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/student/assignments/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_teacher_success(client: TestClient):
    token = admin_get_access_token(client)
    teacher_dict: dict = {
        "username": "teacher_name",
        "email": "teacher@email.com",
        "password": "54321"
    }
    response = client.post("/admin/add-teacher/", json=teacher_dict, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["username"] == "teacher_name"
    assert response.json()["email"] == "teacher@email.com"
    assert response.json()["user_type"] == "TEA"
    assert response.json()["is_active"] == True

def test_add_teacher_bad_mail(client: TestClient):
    token = admin_get_access_token(client)
    teacher_dict: dict = {
        "username": "teacher_name",
        "email": "test@email.com",
        "password": "54321"
    }
    teacher_dict2: dict = {
        "username": "teacher_name1",
        "email": "teacher@email.com",
        "password": "54321"
    }
    client.post("/admin/add-teacher/", json=teacher_dict, headers={"Authorization": f"Bearer {token}"})
    response = client.post("/admin/add-teacher/", json=teacher_dict2, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

def test_add_teacher_bad_user_name(client: TestClient):
    token = admin_get_access_token(client)
    teacher_dict: dict = {
        "username": "test_name",
        "email": "teacher@email.com",
        "password": "54321"
    }
    teacher_dict2: dict = {
        "username": "test_name",
        "email": "teacher1@email.com",
        "password": "54321"
    }
    client.post("/admin/add-teacher/", json=teacher_dict, headers={"Authorization": f"Bearer {token}"})
    response = client.post("/admin/add-teacher/", json=teacher_dict2, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}

def test_pause_teacher_success(client: TestClient):
    token = admin_get_access_token(client)
    teacher_dict: dict = {
        "username": "teacher189_name",
        "email": "teacher189@email.com",
        "password": "54321"
    }
    response = client.post("/admin/add-teacher/", json=teacher_dict, headers={"Authorization": f"Bearer {token}"})
    get_id = response.json()["id"]
    response2 = client.patch(f"/admin/teacher/{get_id}/pause/", headers={"Authorization": f"Bearer {token}"})
    assert response2.status_code == 200
    assert response2.json()["is_active"] == False

def test_pause_teacher_bad_id(client: TestClient):
    token = admin_get_access_token(client)
    response = client.patch(f"/admin/teacher/{190}/pause/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_pause_teacher_bad_user(client: TestClient):
    token = admin_get_access_token(client)
    in_data: dict = {
        "username": "test201_name",
        "email": "test201@email.com",
        "password": "12345",
    }
    response = client.post("/student/create/", json=in_data)
    get_id = response.json()["id"]
    response2 = client.patch(f"/admin/teacher/{get_id}/pause/", headers={"Authorization": f"Bearer {token}"})
    assert response2.status_code == 400
    assert response2.json()["detail"] == "User is not a teacher"

def test_pause_teacher_already_paused(client: TestClient):
    token = admin_get_access_token(client)
    teacher_dict: dict = {
        "username": "teacher101_name",
        "email": "teacher101@email.com",
        "password": "54321"
    }
    temp = client.post("/admin/add-teacher/", json=teacher_dict, headers={"Authorization": f"Bearer {token}"})
    temp_id = temp.json()["id"]
    client.patch(f"/admin/teacher/{temp_id}/pause/", headers={"Authorization": f"Bearer {token}"})
    response = client.patch(f"/admin/teacher/{temp_id}/pause/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "User is already paused"

def test_delete_user_success(client: TestClient):
    token = admin_get_access_token(client)
    in_data: dict = {
        "username": "test190_name",
        "email": "test190@email.com",
        "password": "12345",
    }
    response = client.post("/student/create/", json=in_data)
    response_id = response.json()["id"]
    response2 = client.delete(f"/admin/user/{response_id}/delete/", headers={"Authorization": f"Bearer {token}"})
    assert response2.status_code == 204
    assert not response2.content

def test_delete_user_bad_user(client: TestClient):
    token = admin_get_access_token(client)
    response = client.delete(f"/admin/user/{190}/delete/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

def test_delete_user_bad_admin(client: TestClient):
    token = admin_get_access_token(client)
    admin_user = crud.get_user_by_name(next(main.get_db()), main.ADMIN_USERNAME)
    response = client.delete(f"/admin/user/{admin_user.id}/delete/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Admin cannot be deleted"