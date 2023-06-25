from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from poly.db import get_session
from poly.services import oauth2_scheme


def get_auth_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_session)
):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="No access token"
        )


def get_current_auth_user(user=Depends(get_auth_user)):
    pass
