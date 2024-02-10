from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from poly.db.schema import Roles
from poly.services.permissions import check_permission
from poly.services.roles import get_roles, get_roles_count

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=Roles)
async def get_paginated_roles(
    _: Annotated[str, Depends(check_permission)],
    request: Request,
    id: int = 0,
    per_page: int = 10,
):
    total = await get_roles_count(async_session=request.app.state.async_session)
    if not total:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="There are no existing roles.",
        )

    roles = await get_roles(
        skip_id=id, limit=per_page, async_session=request.app.state.async_session
    )

    return {"roles": roles, "total": total}
