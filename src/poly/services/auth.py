from datetime import datetime, timedelta
from typing import Annotated, Mapping

from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.config import Settings, get_settings
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
    return jwt.encode(
        claims={
            "aud": audience,
            "exp": datetime.utcnow() + timedelta(minutes=expires_in),
            "iss": issuer,
            "sub": username,
        },
        key=secret,
        algorithm="HS256",
    )


async def authenticate(email: str, password: str, session: async_sessionmaker) -> User:
    user = await get_user_by_email(email=email, async_session=session)
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


async def get_active_user(async_session: async_sessionmaker, username: str) -> User:
    user = await get_user_by_name(name=username, async_session=async_session)

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


async def validate_cookie(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    x_username: Annotated[str, Header()],
    poly_refresh_token: Annotated[str | None, Cookie()] = None,
) -> str:  # pragma: no cover
    if not poly_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty token"
        )

    user = await get_active_user(
        async_session=request.app.state.async_session, username=x_username
    )

    claims = validate_jwt(
        audience=settings.access_token_audience,
        issuer=settings.access_token_issuer,
        secret=settings.secret_key,
        subject=user.name,
        token=poly_refresh_token,
    )

    return claims["sub"]


async def validate_access_token(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    token: Annotated[str, Depends(oauth2_scheme)],
    x_username: Annotated[str, Header()],
) -> str:  # pragma: no cover
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty token",
        )

    user = await get_active_user(
        async_session=request.app.state.async_session, username=x_username
    )

    claims = validate_jwt(
        audience=settings.access_token_audience,
        issuer=settings.access_token_issuer,
        secret=settings.secret_key,
        subject=user.name,
        token=token,
    )

    return claims["sub"]
