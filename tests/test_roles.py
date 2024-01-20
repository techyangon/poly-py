import pytest
from fastapi import status


@pytest.mark.asyncio(scope="session")
async def test_empty_branches(client, user):
    response = await client.get(
        "/roles/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "There are no existing roles."


@pytest.mark.asyncio(scope="session")
async def test_get_roles(client, roles, user):
    response = await client.get(
        "/roles/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )

    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["roles"][0]["name"] == roles[0].name
    assert data["roles"][1]["name"] == roles[1].name
    assert data["total"] == 2
