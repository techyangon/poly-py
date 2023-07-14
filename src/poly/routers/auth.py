from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from poly.db import get_session

router = APIRouter(tags=["auth"])


@router.post("/login")
async def authenticate(session: AsyncSession = Depends(get_session)):
    pass
