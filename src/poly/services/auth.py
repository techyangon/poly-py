from typing import Sequence

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from poly.config import get_settings
from poly.db import get_session
from poly.db.models import User
from poly.services import oauth2_scheme
from poly.services.user import get_user

settings = get_settings()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_token(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No access token"
        )
    return ""


async def authenticate(
    email: str, password: str, session: AsyncSession
) -> Sequence[User]:
    user = await get_user(email=email, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if isinstance(user, User):
        if not password_context.verify(password, user.password.strip()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

    return user


async def get_auth_user(
    username: str = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    return {}


async def get_current_auth_user(user=Depends(get_auth_user)):
    return {}
