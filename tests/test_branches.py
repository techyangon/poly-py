import pytest
from fastapi import status

from poly.db.models import Branch


@pytest.mark.asyncio(scope="session")
async def test_empty_branches(client, user):
    response = await client.get(
        "/branches/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data["detail"] == "There are no existing branches."


@pytest.mark.asyncio(scope="session")
async def test_get_paginated_branches(branches, client, user):
    response = await client.get(
        "/branches/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    for branch in data["branches"]:
        assert branch["name"] in [branches[0].name, branches[1].name]
    assert data["total"] == 2


@pytest.mark.asyncio(scope="session")
async def test_get_single_branch_with_wrong_id(branches, client, user):
    response = await client.get(
        "/branches/3",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    data = response.json()

    assert response.status_code == 404
    assert data["detail"] == "Requested branch does not exist."


@pytest.mark.asyncio(scope="session")
async def test_get_single_branch(branches, client, user):
    response = await client.get(
        "/branches/1",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["address"] == "address1"
    assert data["city"] == "city1"
    assert data["created_by"] == user.name
    assert data["id"] == 1
    assert data["name"] == "branch1"
    assert data["state"] == "state1"
    assert data["township"] == "township1"


@pytest.mark.asyncio(scope="session")
async def test_create_new_branch_with_duplicate_name(branches, client, user):
    response = await client.post(
        "/branches/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={"name": "branch1", "address": "address3", "township_id": 1},
    )
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "Branch with name branch1 already exists."


@pytest.mark.asyncio(scope="session")
async def test_create_new_branch_with_empty_values(client, user):
    response = await client.post(
        "/branches/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={"name": "", "address": "", "township_id": ""},
    )
    data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert data["detail"][0]["msg"] == "Value error, name cannot be empty."
    assert data["detail"][1]["msg"] == "Value error, address cannot be empty."
    assert (
        data["detail"][2]["msg"]
        == "Input should be a valid integer, unable to parse string as an integer"
    )


@pytest.mark.asyncio(scope="session")
async def test_create_new_branch_with_non_existent_township(client, user):
    response = await client.post(
        "/branches/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={"name": "branch3", "address": "address3", "township_id": 2},
    )
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "Township does not exist."


@pytest.mark.asyncio(scope="session")
async def test_create_new_branch(branches, client, user):
    response = await client.post(
        "/branches/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={"name": "branch3", "address": "address3", "township_id": 1},
    )
    data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert data["message"] == "branch3 branch is successfully created."


@pytest.mark.asyncio(scope="session")
async def test_update_non_existent_branch(branches, client, user):
    response = await client.put(
        "/branches/4",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={"name": "branch3", "address": "address3", "township_id": 1},
    )
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "Requested branch does not exist."


@pytest.mark.asyncio(scope="session")
async def test_update_branch_with_duplicate_name(branches, client, user):
    response = await client.put(
        "/branches/1",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={"name": "branch2", "address": "address1", "township_id": 1},
    )
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "Branch with name branch2 already exists."


@pytest.mark.asyncio(scope="session")
async def test_update_branch_with_non_existent_township(branches, client, user):
    response = await client.put(
        "/branches/1",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={"name": "branch1", "address": "address1", "township_id": 2},
    )
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "Township does not exist."


@pytest.mark.asyncio(scope="session")
async def test_update_branch(branches, client, db_session, user):
    response = await client.put(
        "/branches/1",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
        json={"name": "branch4", "address": "address3", "township_id": 1},
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["message"] == "Branch is successfully updated."

    async with db_session() as session, session.begin():
        branch = await session.get(Branch, 1)
        assert branch.name == "branch4"


@pytest.mark.asyncio(scope="session")
async def test_delete_branch_with_non_existent_branch(client, user):
    response = await client.delete(
        "/branches/4",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data["detail"] == "Requested branch does not exist."


@pytest.mark.asyncio(scope="session")
async def test_delete_branch(branches, db_session, client, user):
    response = await client.delete(
        "/branches/2",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    data = response.json()

    assert data["message"] == "Branch is successfully deleted."

    async with db_session() as session, session.begin():
        branch = await session.get(Branch, 2)
        assert branch.is_deleted is True
