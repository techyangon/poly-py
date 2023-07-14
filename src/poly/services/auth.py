from typing import Literal

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from poly.config import get_settings
from poly.db import get_session
from poly.services import oauth2_scheme

settings = get_settings()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_password: str) -> Literal[True, False]:
    return password_context.verify(secret=password, hash=hashed_password)


def validate_token(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No access token"
        )
    return ""


async def get_auth_user(
    username: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    return {}


async def get_current_auth_user(user=Depends(get_auth_user)):
    return {}
