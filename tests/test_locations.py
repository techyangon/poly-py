import pytest
from fastapi import status


@pytest.mark.asyncio(scope="session")
async def test_get_locations(city, client, state, township, user):
    response = await client.get(
        "/locations/",
        headers={"Authorization": "Bearer eyabc.def.ghi", "X-Username": user.name},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert data["states"][0]["name"] == state.name
    assert data["states"][0]["cities"][0]["name"] == city.name
    assert data["states"][0]["cities"][0]["townships"][0]["name"] == township.name
