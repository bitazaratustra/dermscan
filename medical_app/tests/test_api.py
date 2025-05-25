# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
from app.config import settings

@pytest.fixture(scope="module")
def test_client():
    # Configurar base de datos de prueba
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)

def test_full_workflow(test_client):
    # Registro de usuario
    response = test_client.post("/auth/register", json={
        "email": "test@dermscan.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    })
    assert response.status_code == 201

    # Login
    login_response = test_client.post("/auth/token", data={
        "username": "test@dermscan.com",
        "password": "SecurePass123!"
    })
    token = login_response.json()["access_token"]

    # Subida de imagen
    with open("tests/test_image.jpg", "rb") as image:
        response = test_client.post(
            "/upload/predict",
            files={"file": ("test_image.jpg", image, "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"}
        )

    assert response.status_code == 200
    assert "diagnosis" in response.json()


def test_invalid_token_access(test_client):
    response = test_client.post(
        "/upload/predict",
        files={"file": ("test.jpg", b"fake_data", "image/jpeg")},
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
