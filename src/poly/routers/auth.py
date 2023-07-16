from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from poly.db import get_session
from poly.db.schema import Token

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
async def authenticate(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    pass
