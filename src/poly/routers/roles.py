from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db import get_session
from poly.db.schema import Roles
from poly.services.permissions import check_permission
from poly.services.roles import get_roles, get_roles_count

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=Roles)
async def get_paginated_roles(
    session: Annotated[async_sessionmaker, Depends(get_session)],
    is_allowed: Annotated[bool, Depends(check_permission)],
    skip: int = 0,
    limit: int = 10,
):
    roles = await get_roles(skip=skip, per_page=limit, async_session=session)
    total = await get_roles_count(async_session=session)

    return {"roles": roles, "total": total}
