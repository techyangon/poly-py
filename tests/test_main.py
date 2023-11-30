import pytest


@pytest.mark.asyncio
async def test_root_without_custom_header(client):
    response = await client.get("/", headers={"Authorization": "Bearer "})
    data = response.json()
    assert response.status_code == 422
    assert data["detail"][0]["loc"] == ["header", "x-username"]


@pytest.mark.asyncio
async def test_root_with_empty_token(client):
    response = await client.get(
        "/", headers={"Authorization": "Bearer ", "X-Username": "user"}
    )
    assert response.status_code == 401
    assert response.json() == {"detail": "Empty token"}


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get(
        "/", headers={"Authorization": "Bearer eyABC.eyDEF.GHI", "X-Username": "user"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Poly"}
