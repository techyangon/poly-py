from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from poly.config import Settings
from poly.db import get_session
from poly.db.models import User
from poly.services import oauth2_scheme
from poly.services.user import get_user

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_token(token: str = Depends(oauth2_scheme)) -> str:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No access token"
        )
    return ""


def generate_token(user: User, expires_in: int, settings: Settings) -> str:
    expires_delta = datetime.utcnow() + timedelta(minutes=expires_in)
    claims = {
        "aud": settings.access_token_audience,
        "exp": expires_delta,
        "iss": settings.access_token_issuer,
        "sub": user.email,
    }
    encoded_jwt = jwt.encode(
        claims=claims, key=settings.secret_key, algorithm=settings.hashing_algorithm
    )
    return encoded_jwt


async def authenticate(email: str, password: str, session: AsyncSession) -> User:
    user = await get_user(email=email, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

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
