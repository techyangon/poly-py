import os

from fastapi.testclient import TestClient

from poly.config import Settings, get_settings
from poly.main import app

client = TestClient(app)


def override_get_settings():
    return Settings(
        db_host=os.getenv("DB_HOST", "localhost"),
        db_name=os.getenv("DB_NAME", "test"),
        db_username=os.getenv("DB_USERNAME", "admin"),
        db_password=os.getenv("DB_PASSWORD", "passwd"),
        db_port=os.getenv("DB_PORT", "5432"),
    )


app.dependency_overrides[get_settings] = override_get_settings


def test_root():
    response = client.get("/", headers={"Authorization": ""})
    assert response.status_code == 401
