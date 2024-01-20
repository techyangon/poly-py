from typing import Annotated

from casbin import AsyncEnforcer
from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.config import Settings, get_settings
from poly.db import get_session
from poly.db.schema import Token
from poly.rbac.models import get_enforcer
from poly.services.auth import authenticate, generate_token, validate_cookie
from poly.services.permissions import get_permissions_by_role

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    enforcer: Annotated[AsyncEnforcer, Depends(get_enforcer)],
    response: Response,
    session: Annotated[async_sessionmaker, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    user = await authenticate(
        email=form_data.username, password=form_data.password, session=session
    )

    access_token = generate_token(
        audience=settings.access_token_audience,
        expires_in=settings.access_token_expiry,
        issuer=settings.access_token_issuer,
        secret=settings.secret_key,
        username=user.name,
    )

    refresh_token = generate_token(
        audience=settings.access_token_audience,
        expires_in=settings.refresh_token_expiry,
        issuer=settings.access_token_issuer,
        secret=settings.secret_key,
        username=user.name,
    )

    # Enforcer returns a list in the form of [[{username}, {rolename}]]
    role = enforcer.get_filtered_named_grouping_policy("g", 0, user.name)[0][1]
    permissions = get_permissions_by_role(enforcer=enforcer, role=role)

    response.set_cookie(key="poly_refresh_token", value=refresh_token)

    return {
        "access_token": access_token,
        "expires_in": settings.access_token_expiry * 60,
        "name": user.name,
        "permissions": permissions,
        "role": role.split("_")[1],  # roles are stored as role_{rolename}
        "token_type": "Bearer",
    }


@router.get("/token", response_model=Token)
async def token(
    settings: Annotated[Settings, Depends(get_settings)],
    username: Annotated[str, Depends(validate_cookie)],
):  # pragma: no cover
    access_token = generate_token(
        audience=settings.access_token_audience,
        expires_in=settings.access_token_expiry,
        issuer=settings.access_token_issuer,
        secret=settings.secret_key,
        username=username,
    )

    return {
        "access_token": access_token,
        "name": username,
        "token_type": "Bearer",
        "expires_in": settings.access_token_expiry * 60,
    }
