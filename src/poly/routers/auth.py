from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from poly.config import Settings, get_settings
from poly.db.schema import Token
from poly.services.auth import authenticate, generate_token, validate_cookie

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    request: Request,
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
):
    user = await authenticate(
        email=form_data.username,
        password=form_data.password,
        session=request.app.state.async_session,
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

    response.set_cookie(key="poly_refresh_token", value=refresh_token)

    return {
        "access_token": access_token,
        "expires_in": settings.access_token_expiry * 60,
        "name": user.name,
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
        "expires_in": settings.access_token_expiry * 60,
        "name": username,
        "token_type": "Bearer",
    }
