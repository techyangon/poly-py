from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db.models import Role


async def get_roles(skip_id: int, limit: int, async_session: async_sessionmaker):
    async with async_session() as session, session.begin():
        result = await session.execute(
            select(Role.id, Role.name)
            .where(Role.id > skip_id)
            .order_by(Role.created_at)
            .limit(limit)
        )
        return result.all()  # pragma: no cover


async def get_roles_count(async_session: async_sessionmaker) -> int:  # pragma: no cover
    async with async_session() as session, session.begin():
        result = await session.execute(select(func.count()).select_from(Role))
        return result.scalar_one()
