from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from poly.config import settings
from poly.db import get_session
from poly.db.models import User
from poly.db.schema import Token
from poly.services.auth import authenticate, generate_token, get_user_from_cookie

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    user = await authenticate(
        email=form_data.username, password=form_data.password, session=session
    )
    access_token = generate_token(
        username=user.name, expires_in=settings.access_token_expiry
    )
    refresh_token = generate_token(
        username=user.name, expires_in=settings.refresh_token_expiry
    )

    response.set_cookie(key="poly_refresh_token", value=refresh_token)

    return {
        "access_token": access_token,
        "name": user.name,
        "token_type": "Bearer",
        "expires_in": settings.access_token_expiry * 60,
    }


@router.get("/token", response_model=Token)
async def token(
    user: Annotated[User, Depends(get_user_from_cookie)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    access_token = generate_token(
        username=user.name, expires_in=settings.access_token_expiry
    )
    return {
        "access_token": access_token,
        "name": user.name,
        "token_type": "Bearer",
        "expires_in": settings.access_token_expiry * 60,
    }
