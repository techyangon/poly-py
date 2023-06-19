from fastapi.testclient import TestClient

from poly.main import app

client = TestClient(app)


def test_root():
    response = client.get("/", headers={"Authorization": ""})
    assert response.status_code == 401
