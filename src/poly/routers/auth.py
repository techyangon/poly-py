from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from poly.db import get_session
from poly.services.auth import authenticate

router = APIRouter(tags=["auth"])


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    user = await authenticate(
        email=form_data.username, password=form_data.password, session=session
    )
    return {"user": user}
