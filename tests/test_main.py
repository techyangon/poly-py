from fastapi.testclient import TestClient

from poly.config import get_settings
from poly.main import app
from tests import override_get_settings

client = TestClient(app)
app.dependency_overrides[get_settings] = override_get_settings


def test_root_with_empty_token():
    response = client.get("/", headers={"Authorization": "Bearer "})
    assert response.status_code == 401
    assert response.json() == {"detail": "No access token"}


app.dependency_overrides = {}
