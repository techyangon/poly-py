import pytest
from fastapi import HTTPException

from poly.services.auth import authenticate


@pytest.mark.asyncio
async def test_authenticate(user, session):
    # incorrect email, correct password
    with pytest.raises(HTTPException) as exc_info:
        await authenticate("user@mail.test", "passwd", session)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect email or password"

    # correct email, incorrect password
    with pytest.raises(HTTPException):
        await authenticate(user.email, "password", session)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect email or password"

    # correct email, correct password
    result = await authenticate(user.email, "passwd", session)
    assert result is not None


@pytest.mark.asyncio
async def test_login(client, user):
    response = await client.post(
        "/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": user.email, "password": "passwd"},
    )
    assert response.status_code == 200
