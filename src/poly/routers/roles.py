from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db import get_session
from poly.db.schema import Roles
from poly.services.permissions import check_permission
from poly.services.roles import get_roles, get_roles_count

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=Roles)
async def get_paginated_roles(
    session: Annotated[async_sessionmaker, Depends(get_session)],
    _: Annotated[bool, Depends(check_permission)],
    skip: int = 0,
    limit: int = 10,
):
    total = await get_roles_count(async_session=session)
    if not total:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No roles are found. Start creating a new role.",
        )

    roles = await get_roles(skip=skip, per_page=limit, async_session=session)

    return {"roles": roles, "total": total}
