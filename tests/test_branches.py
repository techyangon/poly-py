import pytest


@pytest.mark.asyncio(scope="session")
async def test_get_paginated_branches(city, client, branches, state, township, user):
    response = await client.get(
        "/branches/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["branches"][0]["name"] == branches[0].name
    assert data["branches"][0]["address"] == branches[0].address
    assert data["branches"][0]["city"] == city.name
    assert data["branches"][0]["state"] == state.name
    assert data["branches"][0]["township"] == township.name
    assert data["total"] == 1
