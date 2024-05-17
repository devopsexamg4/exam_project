from fastapi.testclient import TestClient
from passlib.context import CryptContext
from main import app
from models import UserType

client = TestClient(app)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

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