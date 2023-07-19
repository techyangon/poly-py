import pytest


@pytest.mark.asyncio
async def test_login(client, user):
    response = await client.post(
        "/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": user.email, "password": "passwd"},
    )
    assert response.status_code == 200
