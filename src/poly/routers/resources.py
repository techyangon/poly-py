from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db import get_session
from poly.db.schema import Resource, Resources
from poly.services.permissions import check_permission
from poly.services.resources import get_all_resources

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/", response_model=Resources)
async def get_paginated_resources(
    session: Annotated[async_sessionmaker, Depends(get_session)],
    _: Annotated[str, Depends(check_permission)],
):
    resource_result = await get_all_resources(async_session=session)
    resources = [Resource(name=resource.name) for resource in resource_result]

    return {"resources": resources}
