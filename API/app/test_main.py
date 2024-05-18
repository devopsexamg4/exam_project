from fastapi.testclient import TestClient
from passlib.context import CryptContext
from main import app
from models import UserType

client = TestClient(app)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_access_token():
    in_data: dict = {
        "username": "test_name",
        "email": "test@email.com",
        "password": "12345",
        "is_active": True
    }
    in_data2: dict = {
        "username": "test_name",
        "password": "12345"
    }
    client.post("/student/create/", json=in_data)
    response = client.post("/login/", form_data=in_data2)
    return response.json()["access_token"]

def test_create_profile_student_success():
    in_data: dict = {
        "user_name": "test_name",
        "email": "test@email.com",
        "password": "12345",
        "is_active": True
    }
    response = client.post("/student/create/", json=in_data)
    assert response.status_code == 200
    assert response.json()["user_name"] == "test_name"
    assert response.json()["email"] == "test@email.com"
    assert response.json()["user_type"] == UserType.STUDENT
    assert response.json()["is_active"] == True
    assert pwd_context.verify(in_data["password"], response.json()["password"])

def test_create_profile_student_bad_user_name():
    in_data: dict = {
        "user_name": "test_name",
        "email": "test@email.com",
        "password": "12345",
        "is_active": True
    }
    in_data2: dict = {
        "user_name": "test_name",
        "email": "test2@email.com",
        "password": "123456",
        "is_active": True
    }
    client.post("/student/create/", json=in_data)
    response = client.post("/student/create/", json=in_data2)
    assert response.status_code == 400
    assert response.json() == {"detail": "Username already registered"}

def test_create_profile_student_bad_email():
    in_data: dict = {
        "user_name": "test_name",
        "email": "test@email.com",
        "password": "12345",
        "is_active": True
    }
    in_data2: dict = {
        "user_name": "test_name2",
        "email": "test@email.com",
        "password": "123456",
        "is_active": True
    }
    client.post("/student/create/", json=in_data)
    response = client.post("student/create/", json=in_data2)
    assert response.status_code == 400
    assert response.json() == {"detail": "Email already registered"}

def test_login_success():
    in_data: dict = {
        "username": "test_name",
        "email": "test@email.com",
        "password": "12345",
        "is_active": True
    }
    in_data2: dict = {
        "username": "test_name",
        "password": "12345"
    }
    client.post("/student/create/", json=in_data)
    response = client.post("/login/", form_data=in_data2)
    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"
    assert "access_token" in response.json()

def test_login_non_existant_user():
    in_data: dict = {
        "username": "test_name",
        "password": "12345"
    }
    response = client.post("/login/", form_data=in_data)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_login_wrong_password_for_user():
    in_data: dict = {
        "username": "test_name",
        "email": "test@email.com",
        "password": "12345",
        "is_active": True
    }
    in_data2: dict = {
        "username": "test_name",
        "password": "123456"
    }
    client.post("/student/create/", json=in_data)
    response = client.post("/login/", form_data=in_data2)
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}

def test_get_assignments_success():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/student/assignments/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# no tests for failing to get assignments, since that would just be testing all the errors from login again
    
def test_submit_solution_success(): # return to this later, how does on pass the file to be tested to the endpoint?
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}