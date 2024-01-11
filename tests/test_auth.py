import pytest
from fastapi import HTTPException

from poly.services.auth import authenticate, validate_username


@pytest.mark.asyncio(scope="session")
async def test_authenticate(user, db_session):
    async with db_session() as session, session.begin():
        # incorrect email, correct password
        with pytest.raises(HTTPException) as exc_info:
            await authenticate(
                email="user@mail.test", password="passwd", session=session
            )
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect email or password"

    async with db_session() as session, session.begin():
        # correct email, incorrect password
        with pytest.raises(HTTPException):
            await authenticate(email=user.email, password="password", session=session)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect email or password"

    async with db_session() as session, session.begin():
        # correct email, correct password
        result = await authenticate(
            email=user.email, password="passwd", session=session
        )
        assert result is not None


@pytest.mark.asyncio(scope="session")
async def test_token_with_empty_cookie(client, user):
    response = await client.get("/token", headers={"X-Username": user.name})
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Empty token"


@pytest.mark.asyncio(scope="session")
async def test_login(client, user):
    response = await client.post(
        "/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": user.email, "password": "passwd"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio(scope="session")
async def test_validate_username(user, inactive_user, db_session):
    async with db_session() as session, session.begin():
        with pytest.raises(HTTPException) as exc_info:
            await validate_username("non_user", session)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User not found"

    async with db_session() as session, session.begin():
        with pytest.raises(HTTPException) as exc_info:
            await validate_username("user.inactive", session)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Inactive user"

    async with db_session() as session, session.begin():
        result = await validate_username("user", session)
        assert result.name == user.name
