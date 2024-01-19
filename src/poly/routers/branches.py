from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db import get_session
from poly.db.schema import Branches
from poly.services.branches import get_branches, get_branches_count
from poly.services.permissions import check_permission

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("/", response_model=Branches)
async def get_paginated_branches(
    session: Annotated[async_sessionmaker, Depends(get_session)],
    _: Annotated[bool, Depends(check_permission)],
    skip: int = 0,
    limit: int = 10,
):
    total = await get_branches_count(async_session=session)
    if not total:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no existing branches.",
        )

    branches = await get_branches(skip=skip, per_page=limit, async_session=session)

    return {"branches": branches, "total": total}
