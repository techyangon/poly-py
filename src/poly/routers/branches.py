from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db import get_session
from poly.db.schema import Branches, NewBranch
from poly.services.branches import get_branches, get_branches_count, save_branch
from poly.services.permissions import check_permission

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("/", response_model=Branches)
async def get_paginated_branches(
    session: Annotated[async_sessionmaker, Depends(get_session)],
    _: Annotated[str, Depends(check_permission)],
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


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_branch(
    session: Annotated[async_sessionmaker, Depends(get_session)],
    branch: NewBranch,
    username: Annotated[str, Depends(check_permission)],
):
    try:
        await save_branch(
            name=branch.name,
            address=branch.address,
            township_id=branch.township_id,
            created_by=username,
            updated_by=username,
            async_session=session,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Branch with name {branch.name} already exists.",
        )

    return {"message": f"{branch.name} branch is successfully created."}
