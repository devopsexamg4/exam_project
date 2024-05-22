from fastapi.testclient import TestClient
from passlib.context import CryptContext
from . import main # app, ADMIN_PASSWORD, ADMIN_USERNAME, get_db 
import subprocess

from datetime import datetime
from . import crud

client = TestClient(main.app)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def test_create_profile_student_success():
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

def test_create_profile_student_bad_user_name():
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

def test_create_profile_student_bad_email():
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

def test_create_profile_student_invalid_email():
    in_data: dict = {
        "username": "testname",
        "email": "testemail.com",
        "password": "12345"
    }
    response = client.post("/student/create/", json=in_data)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid email"}

def test_login_success():
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
    subprocess.run(["rm","sql_app.db"])
