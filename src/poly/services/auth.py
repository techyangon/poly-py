from datetime import datetime, timedelta
from typing import Annotated, Mapping

from fastapi import Depends, Header, HTTPException, status
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from poly.config import Settings, get_settings
from poly.db import get_session
from poly.db.models import User
from poly.services import oauth2_scheme
from poly.services.user import get_user

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def validate_token(
    x_username: Annotated[str, Header()],
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Settings = Depends(get_settings),
) -> Mapping:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty token"
        )
    try:
        return jwt.decode(
            token=token,
            key=settings.secret_key,
            algorithms=settings.hashing_algorithm,
            audience=settings.access_token_audience,
            issuer=settings.access_token_issuer,
            subject=x_username,
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


def generate_token(user: User, expires_in: int, settings: Settings) -> str:
    expires_delta = datetime.utcnow() + timedelta(minutes=expires_in)
    claims = {
        "aud": settings.access_token_audience,
        "exp": expires_delta,
        "iss": settings.access_token_issuer,
        "sub": user.name,
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
    token_claims: Mapping = Depends(validate_token),
    session: AsyncSession = Depends(get_session),
):
    return {}


async def get_current_auth_user(user: User = Depends(get_auth_user)):
    return {}
