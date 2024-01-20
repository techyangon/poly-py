from datetime import datetime

from asyncpg.exceptions import UniqueViolationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
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
        return [
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
            for branch in result.all()
        ]


async def get_branches_count(
    async_session: async_sessionmaker,
) -> int:  # pragma: no cover
    async with async_session() as session, session.begin():
        result = await session.execute(select(func.count()).select_from(Branch))
        return result.scalar_one()


async def save_branch(
    name: str,
    address: str,
    township_id: int,
    created_by: str,
    updated_by: str,
    async_session: async_sessionmaker,
):
    async with async_session() as session:
        try:
            session.add(
                Branch(
                    name=name,
                    address=address,
                    township_id=township_id,
                    created_by=created_by,
                    updated_by=updated_by,
                )
            )
            await session.commit()
        except IntegrityError as error:
            await session.rollback()
            if error.orig and error.orig.__cause__.__class__ == UniqueViolationError:
                raise ValueError
