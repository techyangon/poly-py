from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db import get_session
from poly.db.schema import Resources
from poly.services.resources import get_resources, get_resources_count

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/", response_model=Resources)
async def get_paginated_resources(
    skip: int = 0, limit: int = 10, session: async_sessionmaker = Depends(get_session)
):
    resources = await get_resources(skip=skip, per_page=limit, async_session=session)
    total = await get_resources_count(async_session=session)

    return {"resources": resources, "total": total}
