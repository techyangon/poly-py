from typing import Annotated

from fastapi import APIRouter, Depends, Request

from poly.db.schema import Resources
from poly.services.auth import validate_access_token
from poly.services.resources import get_all_resources

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/", response_model=Resources)
async def get_paginated_resources(
    _: Annotated[str, Depends(validate_access_token)],
    request: Request,
):
    resources = await get_all_resources(async_session=request.app.state.async_session)

    return {"resources": resources}
