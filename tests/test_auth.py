import pytest
from fastapi import HTTPException

from poly.services.auth import authenticate, get_active_user


@pytest.mark.asyncio(scope="session")
async def test_authenticate(db_session, user):
    # incorrect email, correct password
    with pytest.raises(HTTPException) as exc_info:
        await authenticate(
            email="user@mail.test", password="passwd", session=db_session
        )
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect email or password"

    # correct email, incorrect password
    with pytest.raises(HTTPException):
        await authenticate(email=user.email, password="password", session=db_session)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect email or password"

    # correct email, correct password
    result = await authenticate(email=user.email, password="passwd", session=db_session)
    assert result is not None


@pytest.mark.asyncio(scope="session")
async def test_token_with_empty_cookie(client, user):
    response = await client.get("/token", headers={"X-Username": user.name})

    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == "Empty token"


@pytest.mark.asyncio(scope="session")
async def test_login(client, permissions, user):
    response = await client.post(
        "/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": user.email, "password": "passwd"},
    )

    data = response.json()

    assert response.status_code == 200
    assert data["role"] == "admin"
    assert data["permissions"][0] == {"resource": "roles", "permissions": ["GET"]}


@pytest.mark.asyncio(scope="session")
async def test_get_active_user(db_session, inactive_user, user):
    with pytest.raises(HTTPException) as exc_info:
        await get_active_user("non_user", db_session)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User not found"

    with pytest.raises(HTTPException) as exc_info:
        await get_active_user("user.inactive", db_session)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Inactive user"

    result = await get_active_user("user", db_session)
    assert result.name == user.name
