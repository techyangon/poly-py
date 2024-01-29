from datetime import datetime

import pytest


@pytest.mark.asyncio(scope="session")
async def test_get_profile(client, user):
    response = await client.get(
        "/profile/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == user.name
    assert data["role"] == "admin"
    assert data["created_at"] == datetime.isoformat(user.created_at) + "Z"


@pytest.mark.asyncio(scope="session")
async def test_update_password_with_incorrect_current_password(client, user):
    response = await client.put(
        "/profile/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={
            "id": user.id,
            "current_password": "password",
            "new_password": r"\abcde7H",
        },
    )
    data = response.json()

    assert response.status_code == 400
    assert data["detail"] == "Current password is incorrect."


@pytest.mark.asyncio(scope="session")
async def test_update_password_with_invalid_new_passsword(client, settings, user):
    response = await client.put(
        "/profile/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={
            "id": user.id,
            "current_password": settings.admin_password,
            "new_password": r"abcdef7H",
        },
    )
    data = response.json()

    assert response.status_code == 422
    assert (
        data["detail"][0]["msg"]
        == "Value error, Invalid password. Please check the rules again."
    )


@pytest.mark.asyncio(scope="session")
async def test_update_password(client, settings, user):
    response = await client.put(
        "/profile/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={
            "id": user.id,
            "current_password": settings.admin_password,
            "new_password": r"\abcde7H",
        },
    )
    data = response.json()

    assert response.status_code == 200
    assert data["message"] == "User password is updated."
