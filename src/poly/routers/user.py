from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from poly.db.schema import Profile, UserUpdate
from poly.services.auth import password_context, validate_access_token
from poly.services.user import get_user_by_name, update_user

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/", response_model=Profile)
async def get_user_profile(
    request: Request,
    username: Annotated[str, Depends(validate_access_token)],
):
    enforcer = request.app.state.enforcer

    user = await get_user_by_name(
        name=username, async_session=request.app.state.async_session
    )

    if user:
        role = enforcer.get_filtered_named_grouping_policy("g", 0, user.name)[0][1]

        return {
            "created_at": datetime.isoformat(user.created_at) + "Z",
            "email": user.email,
            "id": user.id,
            "name": user.name,
            "role": role.split("_")[1],
        }


@router.put("/")
async def update_user_password(
    request: Request,
    user: UserUpdate,
    username: Annotated[str, Depends(validate_access_token)],
):
    saved_user = await get_user_by_name(
        name=username, async_session=request.app.state.async_session
    )

    # It is already checked in `validate_access_token`. This is to satisfy pyright.
    if not saved_user:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested user does not exist.",
        )

    if not password_context.verify(user.current_password, saved_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    user.new_password = password_context.hash(user.new_password)
    await update_user(fields=user, async_session=request.app.state.async_session)

    return {"message": "User password is updated."}
