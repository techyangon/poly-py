import pytest
from fastapi import status

from poly import __version__


@pytest.mark.asyncio(scope="session")
async def test_root_without_custom_header(client):
    response = await client.get("/", headers={"Authorization": "Bearer "})

    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data["detail"][0]["loc"] == ["header", "x-username"]


@pytest.mark.asyncio(scope="session")
async def test_root_with_empty_token(client, user):
    response = await client.get(
        "/", headers={"Authorization": "Bearer ", "X-Username": user.name}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Empty token"}


@pytest.mark.asyncio(session="session")
async def test_root(client, user):
    response = await client.get(
        "/", headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name}
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["message"] == "Welcome to Poly"


@pytest.mark.asyncio(session="session")
async def test_version(client):
    response = await client.get("/version")
    data = response.json()

    assert data["message"] == __version__
