import pytest
from fastapi import status


@pytest.mark.asyncio(scope="session")
async def test_get_permissions(client, user):
    response = await client.get(
        "/permissions/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["role"] == "admin"
    for permission in data["permissions"]:
        assert permission["resource"] in ["branches", "locations", "resources", "roles"]
