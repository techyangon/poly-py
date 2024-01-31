from typing import Annotated

from casbin import AsyncEnforcer
from fastapi import APIRouter, Depends

from poly.db.schema import Permissions
from poly.rbac.models import get_enforcer
from poly.services.auth import validate_access_token
from poly.services.permissions import get_permissions_by_role

router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.get("/", response_model=Permissions)
async def get_permissions(
    enforcer: Annotated[AsyncEnforcer, Depends(get_enforcer)],
    username: Annotated[str, Depends(validate_access_token)],
):
    role = enforcer.get_filtered_named_grouping_policy("g", 0, username)[0][1]
    permissions = get_permissions_by_role(enforcer=enforcer, role=role)

    return {"role": role.split("_")[1], "permissions": permissions}
