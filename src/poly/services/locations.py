from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db.models import City, State, Township


async def save_state(name: str, async_session: async_sessionmaker):
    async with async_session() as session, session.begin():
        session.add(State(name=name))


async def get_state_by_name(
    name: str, async_session: async_sessionmaker
) -> Optional[State]:
    async with async_session() as session, session.begin():
        result = await session.scalars(select(State).where(State.name == name))
        return result.one_or_none()


async def save_city(name: str, state_id: int, async_session: async_sessionmaker):
    async with async_session() as session, session.begin():
        session.add(City(name=name, state_id=state_id))


async def get_city_by_name(
    name: str, async_session: async_sessionmaker
) -> Optional[City]:
    async with async_session() as session, session.begin():
        result = await session.scalars(select(City).where(City.name == name))
        return result.one_or_none()


async def save_townships(
    townships: list[str], city_id: int, async_session: async_sessionmaker
):
    pending_tsps = []
    for tsp in townships:
        pending_tsps.append(Township(name=tsp, city_id=city_id))

    async with async_session() as session, session.begin():
        session.add_all(pending_tsps)
