from typing import Annotated, Literal

from casbin import AsyncEnforcer
from fastapi import Depends, Request

from poly.rbac.models import get_enforcer
from poly.services.auth import validate_access_token


async def check_permission(
    request: Request,
    username: Annotated[str, Depends(validate_access_token)],
    enforcer: Annotated[AsyncEnforcer, Depends(get_enforcer)],
) -> Literal[True, False]:  # pragma: no cover
    return enforcer.enforce(username, request.url.path.strip("/"), request.method)


def get_permissions_by_role(enforcer: AsyncEnforcer, role: str) -> list[dict]:
    role_policies = enforcer.get_filtered_named_policy("p", 0, role)
    resources = set([policy[1] for policy in role_policies])

    permissions_per_resource = []
    for resource in resources:
        resource_permissions = filter(
            lambda permission: permission[1] == resource, role_policies
        )

        permissions = [permission[2] for permission in resource_permissions]
        permissions_per_resource.append(
            {"resource": resource, "permissions": permissions}
        )

    return permissions_per_resource
