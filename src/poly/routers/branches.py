from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db import get_session
from poly.db.schema import BranchAbbr, Branches, NewBranch
from poly.services.branches import (
    delete_branch,
    get_branch_by_id,
    get_branch_by_id_with_location,
    get_branches,
    get_branches_count,
    save_branch,
    update_branch,
)
from poly.services.permissions import check_permission

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("/", response_model=Branches)
async def get_paginated_branches(
    session: Annotated[async_sessionmaker, Depends(get_session)],
    _: Annotated[str, Depends(check_permission)],
    id: int = 0,
    per_page: int = 10,
):
    total = await get_branches_count(async_session=session)
    if not total:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no existing branches.",
        )

    branches = await get_branches(skip_id=id, limit=per_page, async_session=session)

    return {"branches": branches, "total": total}


@router.get("/{branch_id}", response_model=BranchAbbr)
async def get_single_branch(
    branch_id: int,
    session: Annotated[async_sessionmaker, Depends(get_session)],
):
    branch = await get_branch_by_id_with_location(id=branch_id, async_session=session)
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested branch does not exist.",
        )
    return {
        "address": branch.address,
        "city": branch.township.city.id,
        "created_by": branch.created_by,
        "id": branch.id,
        "name": branch.name,
        "state": branch.township.city.state.id,
        "township": branch.township.id,
        "updated_at": datetime.isoformat(branch.updated_at) + "Z",
    }


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
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    return {"message": f"{branch.name} branch is successfully created."}


@router.put("/{branch_id}")
async def update_existing_branch(
    branch: NewBranch,
    branch_id: int,
    session: Annotated[async_sessionmaker, Depends(get_session)],
    username: Annotated[str, Depends(check_permission)],
):
    saved_branch = await get_branch_by_id(id=branch_id, async_session=session)
    if not saved_branch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested branch does not exist.",
        )

    try:
        await update_branch(
            id=branch_id,
            name=branch.name,
            address=branch.address,
            township_id=branch.township_id,
            updated_by=username,
            async_session=session,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    return {"message": "Branch is successfully updated."}


@router.delete("/{branch_id}")
async def delete_existing_branch(
    branch_id: int,
    session: Annotated[async_sessionmaker, Depends(get_session)],
    _: Annotated[str, Depends(check_permission)],
):
    saved_branch = await get_branch_by_id(id=branch_id, async_session=session)
    if not saved_branch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested branch does not exist.",
        )

    await delete_branch(id=branch_id, async_session=session)

    return {"message": "Branch is successfully deleted."}
