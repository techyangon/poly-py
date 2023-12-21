import pytest
from fastapi import HTTPException

from poly.services.auth import authenticate, validate_username


@pytest.mark.asyncio
async def test_authenticate(user, async_session):
    # incorrect email, correct password
    async with async_session() as session, session.begin():
        with pytest.raises(HTTPException) as exc_info:
            await authenticate("user@mail.test", "passwd", session)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect email or password"

    # correct email, incorrect password
    async with async_session() as session, session.begin():
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


@pytest.mark.asyncio
async def test_token(client, user):
    response = await client.get("/token", headers={"X-Username": "user"})
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == user.name


@pytest.mark.asyncio
async def test_validate_username(user, inactive_user, async_session):
    async with async_session() as session, session.begin():
        with pytest.raises(HTTPException) as exc_info:
            await validate_username("non_user", session)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User not found"

    async with async_session() as session, session.begin():
        with pytest.raises(HTTPException) as exc_info:
            await validate_username("user.inactive", session)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Inactive user"

    async with async_session() as session, session.begin():
        result = await validate_username("user", session)
        assert result.name == user.name
