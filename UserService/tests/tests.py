import pytest
from fastapi.testclient import TestClient
from main import app
from database import Base, engine, SessionLocal
from models.user import User

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_register_user(setup_database):
    response = client.post(
        "/register",
        json={
            "username": "testuser",
            "password": "password123",
            "email": "testuser@example.com",
            "profile_picture": None,
            "background_picture": None,
            "description": "Test user",
            "skills": [{"name": "Python", "level": 5}],
            "experience": [
                {
                    "employer": "Company A",
                    "position": "Developer",
                    "start_date": "2021-01-01",
                    "end_date": "2022-01-01",
                    "is_current": False,
                    "description": "Developed cool stuff."
                }
            ],
            "certifications": ["AWS Certified Developer"],
            "availability": "Full-time"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_login_user(setup_database):
    client.post(
        "/register",
        json={"username": "testuser2", "password": "password123"}
    )
    response = client.post(
        "/login",
        json={"username": "testuser2", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_get_current_user(setup_database):
    client.post(
        "/register",
        json={"username": "testuser3", "password": "password123"}
    )
    response = client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser3"

def test_update_user(setup_database):
    client.post(
        "/register",
        json={"username": "testuser4", "password": "password123"}
    )
    update_response = client.put(
        "/users/me",
        json={
            "username": "updateduser",
            "email": "updateduser@example.com",
            "description": "Updated description",
            "skills": [{"name": "FastAPI", "level": 4}]
        }
    )
    assert update_response.status_code == 200
    assert update_response.json()["username"] == "updateduser"
    assert update_response.json()["email"] == "updateduser@example.com"
