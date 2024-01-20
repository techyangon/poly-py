import pytest
from fastapi import status


@pytest.mark.asyncio(scope="session")
async def test_get_paginated_branches(branches, city, client, state, township, user):
    response = await client.get(
        "/branches/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["branches"][0]["name"] == branches[0].name
    assert data["branches"][0]["address"] == branches[0].address
    assert data["branches"][0]["city"] == city.name
    assert data["branches"][0]["state"] == state.name
    assert data["branches"][0]["township"] == township.name
    assert data["total"] == 1


@pytest.mark.asyncio(scope="session")
async def test_create_new_branch_with_duplicate_name(branches, client, township, user):
    response = await client.post(
        "/branches/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={"name": "branch1", "address": "address2", "township_id": 1},
    )
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "Branch with name branch1 already exists."


@pytest.mark.asyncio(scope="session")
async def test_create_new_branch_with_empty_values(client, user):
    response = await client.post(
        "/branches/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={"name": "", "address": "", "township_id": 1},
    )
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data["detail"][0]["msg"] == "Value error, name cannot be empty."
    assert data["detail"][1]["msg"] == "Value error, address cannot be empty."
