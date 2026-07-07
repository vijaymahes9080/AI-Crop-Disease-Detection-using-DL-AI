# tests/test_backend.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.api.dependencies.database import get_db
from app.models.database import Base

# Setup clean in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_user_flow():
    # 1. Test registration
    reg_response = client.post("/api/v1/auth/register", json={
        "phone_number": "+919999999999",
        "name": "Test Farmer",
        "password": "securepassword123"
    })
    assert reg_response.status_code == 201
    assert "access_token" in reg_response.json()
    
    # 2. Test login
    login_response = client.post("/api/v1/auth/login", data={
        "username": "+919999999999",
        "password": "securepassword123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # 3. Test history endpoint authentication guard
    history_response = client.get(
        "/api/v1/scans/history",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert history_response.status_code == 200
    assert isinstance(history_response.json(), list)
