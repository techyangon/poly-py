from datetime import datetime, timedelta
from typing import Annotated, Mapping

from fastapi import Cookie, Depends, Header, HTTPException, status
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from poly.config import Settings, get_settings
from poly.db import get_session
from poly.db.models import User
from poly.services import oauth2_scheme
from poly.services.user import get_user_by_email, get_user_by_name

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_jwt(
    audience: str,
    issuer: str,
    secret: str,
    subject: str,
    token: str,
) -> Mapping:  # pragma: no cover
    try:
        return jwt.decode(
            algorithms="HS256",
            audience=audience,
            issuer=issuer,
            key=secret,
            subject=subject,
            token=token,
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired token"
        )
    except JWTClaimsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid claims"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def generate_token(
    audience: str,
    expires_in: int,
    issuer: str,
    secret: str,
    username: str,
) -> str:
    expires_delta = datetime.utcnow() + timedelta(minutes=expires_in)
    claims = {
        "aud": audience,
        "exp": expires_delta,
        "iss": issuer,
        "sub": username,
    }
    encoded_jwt = jwt.encode(claims=claims, key=secret, algorithm="HS256")
    return encoded_jwt


async def authenticate(email: str, password: str, session: AsyncSession) -> User:
    user = await get_user_by_email(email=email, session=session)
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


async def validate_username(username: str, session: AsyncSession):
    user = await get_user_by_name(name=username, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user


async def get_active_user(
    x_username: Annotated[str, Header()],
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty token"
        )

    claims = validate_jwt(
        audience=settings.access_token_audience,
        issuer=settings.access_token_issuer,
        secret=settings.secret_key,
        subject=x_username,
        token=token,
    )
    return await validate_username(username=claims["sub"], session=session)


async def get_active_user_from_cookie(
    x_username: Annotated[str, Header()],
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    poly_refresh_token: Annotated[str | None, Cookie()] = None,
) -> User:
    if not poly_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty token"
        )

    claims = validate_jwt(
        audience=settings.access_token_audience,
        issuer=settings.access_token_issuer,
        secret=settings.secret_key,
        subject=x_username,
        token=poly_refresh_token,
    )
    return await validate_username(username=claims["sub"], session=session)
