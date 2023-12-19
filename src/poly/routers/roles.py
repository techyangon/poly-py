from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from poly.db import get_session
from poly.db.schema import Roles
from poly.services.roles import get_roles, get_roles_count

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=Roles)
async def get_paginated_roles(
    skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)
):
    roles = await get_roles(skip=skip, per_page=limit, session=session)
    total = await get_roles_count(session=session)

    return {"roles": roles, "total": total}
