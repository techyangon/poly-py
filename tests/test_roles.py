import pytest


@pytest.mark.asyncio
async def test_get_roles(client, roles):
    response = await client.get(
        "/roles/", headers={"Authorization": "Bearer eyabc.def.ghi"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["roles"][0]["name"] == roles[0].name
    assert data["roles"][1]["name"] == roles[1].name
    assert data["total"] == 2
