from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db.models import User
from poly.db.schema import UserUpdate


async def get_user_by_email(
    email: str, async_session: async_sessionmaker
) -> User | None:
    async with async_session() as session, session.begin():
        result = await session.scalars(select(User).where(User.email == email))
        return result.one_or_none()


async def get_user_by_name(name: str, async_session: async_sessionmaker) -> User | None:
    async with async_session() as session, session.begin():
        result = await session.scalars(select(User).where(User.name == name))
        return result.one_or_none()


async def update_user(
    fields: UserUpdate, async_session: async_sessionmaker
):  # pragma: no cover
    async with async_session() as session, session.begin():
        user = await session.get(User, fields.id)
        for k, v in iter(fields):
            setattr(user, k, v)
        session.add(user)
