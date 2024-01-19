import pytest


@pytest.mark.asyncio(scope="session")
async def test_get_resources(client, resources, user):
    response = await client.get(
        "/resources/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resources"][0]["name"] == resources[0].name
    assert data["resources"][1]["name"] == resources[1].name
