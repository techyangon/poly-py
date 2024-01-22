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
