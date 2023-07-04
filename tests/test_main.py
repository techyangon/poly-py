import pytest


@pytest.mark.asyncio
async def test_root_with_empty_token(client):
    response = await client.get("/", headers={"Authorization": "Bearer "})
    assert response.status_code == 401
    assert response.json() == {"detail": "No access token"}
