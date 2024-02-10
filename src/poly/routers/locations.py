from typing import Annotated

from fastapi import APIRouter, Depends, Request

from poly.db.schema import Locations
from poly.services.auth import validate_access_token
from poly.services.locations import get_all_locations

router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/", response_model=Locations)
async def get_locations(
    _: Annotated[str, Depends(validate_access_token)],
    request: Request,
):
    states = await get_all_locations(async_session=request.app.state.async_session)
    return {"states": states}
