from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload

from poly.db.models import City, State, Township


async def get_all_locations(async_session: async_sessionmaker) -> list[State]:
    async with async_session() as session, session.begin():
        result = await session.scalars(
            select(State)
            .options(
                joinedload(State.cities)
                .load_only(City.name)
                .subqueryload(City.townships)
                .load_only(Township.name)
            )
            .order_by(State.created_at)
        )
        return result.unique().all()  # pragma: no cover


async def save_city(
    name: str, state: str, async_session: async_sessionmaker
):  # pragma: no cover
    async with async_session() as session, session.begin():
        state_id = await session.scalar(select(State.id).where(State.name == state))

        session.add(City(name=name, state_id=state_id))


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
        city_id = await session.scalar(select(City.id).where(City.name == city))

        session.add_all([Township(name=tsp, city_id=city_id) for tsp in townships])
