from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db.models import Resource


async def get_all_resources(
    async_session: async_sessionmaker,
) -> Sequence[Resource]:  # pragma: no cover
    async with async_session() as session, session.begin():
        result = await session.scalars(select(Resource).order_by(Resource.created_at))
        return result.all()
