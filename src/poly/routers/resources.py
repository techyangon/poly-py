from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from poly.db import get_session
from poly.db.schema import Resources
from poly.services.resources import get_resources, get_resources_count

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("/", response_model=Resources)
async def get_paginated_resources(
    skip: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)
):
    resources = await get_resources(skip=skip, per_page=limit, session=session)
    total = await get_resources_count(session=session)

    return {"resources": resources, "total": total}
