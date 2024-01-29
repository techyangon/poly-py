from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.db import get_session
from poly.db.schema import Locations
from poly.services.auth import validate_access_token
from poly.services.locations import get_all_locations

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/", response_model=Locations)
async def get_locations(
    session: Annotated[async_sessionmaker, Depends(get_session)],
    _: Annotated[bool, Depends(validate_access_token)],
):
    states = await get_all_locations(async_session=session)
    return {"states": states}
