from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from poly.db.schema import BranchDetails, Branches, NewBranch
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
    _: Annotated[str, Depends(check_permission)],
    request: Request,
    id: int = 0,
    per_page: int = 10,
):
    total = await get_branches_count(async_session=request.app.state.async_session)
    if not total:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no existing branches.",
        )

    branches = await get_branches(
        skip_id=id, limit=per_page, async_session=request.app.state.async_session
    )

    return {"branches": branches, "total": total}


@router.get("/{branch_id}", response_model=BranchDetails)
async def get_single_branch(
    _: Annotated[str, Depends(check_permission)],
    branch_id: int,
    request: Request,
):
    branch = await get_branch_by_id_with_location(
        id=branch_id, async_session=request.app.state.async_session
    )
    if not branch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested branch does not exist.",
        )
    return {
        "address": branch.address,
        "city": branch.township.city.id,
        "created_at": datetime.isoformat(branch.created_at) + "Z",
        "created_by": branch.created_by,
        "id": branch.id,
        "name": branch.name,
        "state": branch.township.city.state.id,
        "township": branch.township.id,
        "updated_at": datetime.isoformat(branch.updated_at) + "Z",
        "updated_by": branch.updated_by,
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_branch(
    branch: NewBranch,
    request: Request,
    username: Annotated[str, Depends(check_permission)],
):
    try:
        await save_branch(
            name=branch.name,
            address=branch.address,
            township_id=branch.township_id,
            created_by=username,
            updated_by=username,
            async_session=request.app.state.async_session,
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
    request: Request,
    username: Annotated[str, Depends(check_permission)],
):
    saved_branch = await get_branch_by_id(
        id=branch_id, async_session=request.app.state.async_session
    )
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
            async_session=request.app.state.async_session,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )

    return {"message": "Branch is successfully updated."}


@router.delete("/{branch_id}")
async def delete_existing_branch(
    _: Annotated[str, Depends(check_permission)],
    branch_id: int,
    request: Request,
):
    saved_branch = await get_branch_by_id(
        id=branch_id, async_session=request.app.state.async_session
    )
    if not saved_branch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested branch does not exist.",
        )

    # TODO: update who made the change
    await delete_branch(id=branch_id, async_session=request.app.state.async_session)

    return {"message": "Branch is successfully deleted."}
