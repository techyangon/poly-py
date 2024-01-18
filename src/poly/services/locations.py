from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload

from poly.db.models import City, State, Township
from poly.db.schema import (
    City as CityResponse,
    State as StateResponse,
    Township as TownshipResponse,
)


async def get_all_locations(async_session: async_sessionmaker) -> list[StateResponse]:
    async with async_session() as session, session.begin():
        result = await session.scalars(
            select(State)
            .options(joinedload(State.cities).subqueryload(City.townships))
            .order_by(State.created_at)
        )
        return map_to_response_model(result=result.unique().all())


async def save_city(
    name: str, state: str, async_session: async_sessionmaker
):  # pragma: no cover
    async with async_session() as session, session.begin():
        result = await session.scalars(select(State).where(State.name == state))
        saved_state = result.one()

        session.add(City(name=name, state_id=saved_state.id))


async def save_state_and_city(
    city: str, state: str, async_session: async_sessionmaker
):  # pragma: no cover
    async with async_session() as session, session.begin():
        pending_state = State(name=state)
        session.add(pending_state)

        await session.flush()

        session.add(City(name=city, state_id=pending_state.id))


async def save_townships(
    city: str, townships: list[str], async_session: async_sessionmaker
):  # pragma: no cover
    async with async_session() as session, session.begin():
        result = await session.scalars(select(City).where(City.name == city))
        saved_city = result.one()

        pending_tsps = [Township(name=tsp, city_id=saved_city.id) for tsp in townships]

        session.add_all(pending_tsps)


def map_to_response_model(result: Sequence[State]) -> list[StateResponse]:
    states = []
    for state in result:
        cities = []
        for city in state.cities:
            townships = [
                TownshipResponse(name=tsp.name, value=tsp.id) for tsp in city.townships
            ]
            cities.append(
                CityResponse(name=city.name, value=city.id, townships=townships)
            )

        states.append(StateResponse(name=state.name, value=state.id, cities=cities))

    return states
