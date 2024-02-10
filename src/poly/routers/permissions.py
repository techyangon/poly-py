from typing import Annotated

from fastapi import APIRouter, Depends, Request

from poly.db.schema import Permissions
from poly.services.auth import validate_access_token
from poly.services.permissions import get_permissions_by_role

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("/", response_model=Permissions)
async def get_permissions(
    request: Request,
    username: Annotated[str, Depends(validate_access_token)],
):
    enforcer = request.app.state.enforcer

    role = enforcer.get_filtered_named_grouping_policy("g", 0, username)[0][1]
    permissions = await get_permissions_by_role(enforcer=enforcer, role=role)

    return {"role": role.split("_")[1], "permissions": permissions}
