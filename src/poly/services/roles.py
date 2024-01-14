from datetime import datetime
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db.models import Role
from poly.db.schema import Role as RoleResponse


async def get_roles(
    skip: int, per_page: int, async_session: async_sessionmaker
) -> list[RoleResponse]:
    query = select(Role).order_by(Role.created_at).offset(skip).limit(per_page)
    async with async_session() as session, session.begin():
        result = await session.scalars(query)
        return map_to_response_model(result.all())


async def get_roles_count(async_session: async_sessionmaker) -> int:
    query = select(func.count()).select_from(Role)
    async with async_session() as session, session.begin():
        result = await session.execute(query)
        return result.scalar_one()


def map_to_response_model(result: Sequence[Role]) -> list[RoleResponse]:
    roles = []
    for role in result:
        roles.append(
            RoleResponse(
                name=role.name,  # pyright: ignore
                created_at=datetime.isoformat(role.created_at) + "Z",
                created_by=role.created_by,  # pyright: ignore
                updated_at=datetime.isoformat(role.updated_at) + "Z",
                updated_by=role.updated_by,  # pyright: ignore
            )
        )
    return roles
