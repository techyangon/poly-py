from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db.models import User


async def get_user_by_email(
    email: str, async_session: async_sessionmaker
) -> User | None:
    query = select(User).where(User.email == email)

    async with async_session() as session, session.begin():
        result = await session.scalars(query)
        return result.one_or_none()


async def get_user_by_name(name: str, async_session: async_sessionmaker) -> User | None:
    query = select(User).where(User.name == name)

    async with async_session() as session, session.begin():
        result = await session.scalars(query)
        return result.one_or_none()
