from datetime import datetime
from typing import Optional

from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import joinedload

from poly.db.models import Branch, City, State, Township
from poly.db.schema import Branch as BranchResponse


async def get_branches(
    skip_id: int, limit: int, async_session: async_sessionmaker
) -> list[BranchResponse]:
    async with async_session() as session, session.begin():
        result = await session.scalars(
            select(Branch)
            .options(
                joinedload(Branch.township)
                .load_only(Township.name)
                .joinedload(Township.city)
                .load_only(City.name)
                .joinedload(City.state)
                .load_only(State.name)
            )
            .where(Branch.is_deleted.is_(False))
            .where(Branch.id > skip_id)
            .order_by(Branch.created_at)
            .limit(limit)
        )
        return [
            BranchResponse(
                id=branch.id,
                name=branch.name,
                address=branch.address,
                township=branch.township.name,
                city=branch.township.city.name,
                state=branch.township.city.state.name,
            )
            for branch in result.all()
        ]


async def get_branch_by_id(
    id: int, async_session: async_sessionmaker
) -> Optional[Branch]:
    async with async_session() as session, session.begin():
        return await session.get(Branch, id)


async def get_branch_by_id_with_location(
    id: int, async_session: async_sessionmaker
) -> Optional[Branch]:  # pragma: no cover
    async with async_session() as session, session.begin():
        result = await session.scalars(
            select(Branch)
            .options(
                joinedload(Branch.township)
                .load_only(Township.id)
                .joinedload(Township.city)
                .load_only(City.id)
                .joinedload(City.state)
                .load_only(State.id)
            )
            .where(Branch.id == id)
            .where(Branch.is_deleted.is_(False))
            .limit(1)
        )
        return result.one_or_none()


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
        except IntegrityError as error:  # pragma: no cover
            await session.rollback()
            if error.orig:
                if error.orig.__cause__.__class__ == UniqueViolationError:
                    raise ValueError(f"Branch with name {name} already exists.")

                if error.orig.__cause__.__class__ == ForeignKeyViolationError:
                    raise ValueError("Township does not exist.")


async def update_branch(
    id: int,
    name: str,
    address: str,
    township_id: int,
    updated_by: str,
    async_session: async_sessionmaker,
):  # pragma: no cover
    async with async_session() as session:
        try:
            branch = await session.get(Branch, id)
            branch.name, branch.address, branch.township_id, branch.updated_by = (
                name,
                address,
                township_id,
                updated_by,
            )
            await session.commit()
        except IntegrityError as error:
            await session.rollback()
            if error.orig:
                if error.orig.__cause__.__class__ == UniqueViolationError:
                    raise ValueError(f"Branch with name {name} already exists.")

                if error.orig.__cause__.__class__ == ForeignKeyViolationError:
                    raise ValueError("Township does not exist.")


async def delete_branch(id: int, async_session: async_sessionmaker):  # pragma: no cover
    async with async_session() as session, session.begin():
        branch = await session.get(Branch, id)
        branch.is_deleted = True
