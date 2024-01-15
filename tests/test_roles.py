import pytest


@pytest.mark.asyncio(scope="session")
async def test_get_roles(client, roles, user):
    response = await client.get(
        "/roles/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )

    data = response.json()

    assert data["roles"][0]["name"] == roles[0].name
    assert data["roles"][1]["name"] == roles[1].name
    assert data["total"] == 2
