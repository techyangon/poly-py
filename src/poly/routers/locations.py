from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db import get_session
from poly.db.schema import Locations
from poly.services.locations import get_all_locations
from poly.services.permissions import check_permission

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/", response_model=Locations)
async def get_locations(
    session: Annotated[async_sessionmaker, Depends(get_session)],
    _: Annotated[bool, Depends(check_permission)],
):
    states = await get_all_locations(async_session=session)
    return {"states": states}
