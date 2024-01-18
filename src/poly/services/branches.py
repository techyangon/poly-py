from datetime import datetime
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload

from poly.db.models import Branch, City, Township
from poly.db.schema import Branch as BranchResponse


async def get_branches(
    skip: int, per_page: int, async_session: async_sessionmaker
) -> list[BranchResponse]:
    async with async_session() as session, session.begin():
        result = await session.scalars(
            select(Branch)
            .options(
                joinedload(Branch.township)
                .joinedload(Township.city)
                .joinedload(City.state)
            )
            .order_by(Branch.created_at)
            .offset(skip)
            .limit(per_page)
        )
        return map_to_response_model(result=result.all())


async def get_branches_count(
    async_session: async_sessionmaker,
) -> int:  # pragma: no cover
    async with async_session() as session, session.begin():
        result = await session.execute(select(func.count()).select_from(Branch))
        return result.scalar_one()


def map_to_response_model(result: Sequence[Branch]) -> list[BranchResponse]:
    branches = []

    for branch in result:
        branches.append(
            BranchResponse(
                name=branch.name,
                address=branch.address,
                township=branch.township.name,
                city=branch.township.city.name,
                state=branch.township.city.state.name,
                created_at=datetime.isoformat(branch.created_at) + "Z",
                created_by=branch.created_by,
                updated_at=datetime.isoformat(branch.updated_at) + "Z",
                updated_by=branch.updated_by,
            )
        )

    return branches
