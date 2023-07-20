from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from poly.db import get_session
from poly.db.schema import Token
from poly.services.auth import authenticate, generate_access_token

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    user = await authenticate(
        email=form_data.username, password=form_data.password, session=session
    )
    token_details = generate_access_token(user)

    return {
        "access_token": token_details["token"],
        "token_type": "Bearer",
        "expires_in": token_details["expires"],
    }
