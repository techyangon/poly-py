from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db.models import Resource
from poly.db.schema import Resource as ResourceResponse


async def get_resources(async_session: async_sessionmaker) -> list[ResourceResponse]:
    async with async_session() as session, session.begin():
        result = await session.scalars(select(Resource).order_by(Resource.created_at))
        resources = result.all()
        return [ResourceResponse(name=resource.name) for resource in resources]


async def get_all_resources(
    async_session: async_sessionmaker,
) -> Sequence[Resource]:  # pragma: no cover
    async with async_session() as session, session.begin():
        result = await session.scalars(select(Resource).order_by(Resource.created_at))
        return result.all()
