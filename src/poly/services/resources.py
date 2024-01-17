from datetime import datetime
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db.models import Resource
from poly.db.schema import Resource as ResourceResponse


async def get_resources(
    skip: int, per_page: int, async_session: async_sessionmaker
) -> list[ResourceResponse]:
    async with async_session() as session, session.begin():
        result = await session.scalars(
            select(Resource).order_by(Resource.created_at).offset(skip).limit(per_page)
        )
        return map_to_response_model(result.all())


async def get_all_resources(
    async_session: async_sessionmaker,
) -> Sequence[Resource]:  # pragma: no cover
    async with async_session() as session, session.begin():
        result = await session.scalars(select(Resource).order_by(Resource.created_at))
        return result.all()


async def get_resources_count(async_session: async_sessionmaker) -> int:
    async with async_session() as session, session.begin():
        result = await session.execute(select(func.count()).select_from(Resource))
        return result.scalar_one()


def map_to_response_model(result: Sequence[Resource]) -> list[ResourceResponse]:
    resources = []

    for resource in result:
        resources.append(
            ResourceResponse(
                name=resource.name,  # pyright: ignore
                created_at=datetime.isoformat(resource.created_at) + "Z",
                created_by=resource.created_by,  # pyright: ignore
                updated_at=datetime.isoformat(resource.updated_at) + "Z",
                updated_by=resource.updated_by,  # pyright: ignore
            )
        )
    return resources
