import pytest


@pytest.mark.asyncio(scope="session")
async def test_get_resources(client, resources):
    response = await client.get(
        "/resources/", headers={"Authorization": "Bearer eyabc.def.ghi"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["resources"][0]["name"] == resources[0].name
    assert data["resources"][1]["name"] == resources[1].name
    assert data["total"] == 2
