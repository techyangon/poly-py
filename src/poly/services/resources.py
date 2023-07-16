from datetime import datetime
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from poly.db.models import Resource
from poly.db.schema import Resource as ResourceResponse


async def get_resources(
    skip: int, per_page: int, session: AsyncSession
) -> list[ResourceResponse]:
    query = select(Resource).offset(skip).limit(per_page)
    result = await session.scalars(query)
    return map_to_response_model(result.all())


async def get_resources_count(session: AsyncSession) -> int:
    query = select(func.count()).select_from(Resource)
    result = await session.execute(query)
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
