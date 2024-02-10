from typing import Annotated

from casbin import AsyncEnforcer
from fastapi import Depends, HTTPException, Request, status

from poly.services.auth import validate_access_token


async def check_permission(
    request: Request,
    username: Annotated[str, Depends(validate_access_token)],
) -> str:
    enforcer = request.app.state.enforcer

    is_allowed = enforcer.enforce(
        username, request.url.path.split("/")[1], request.method
    )
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized to access this resource.",
        )

    return username


async def get_permissions_by_role(enforcer: AsyncEnforcer, role: str) -> list[dict]:
    # Returns a list in the form of [[{role_name}, {resource}, {action}]]
    role_policies = enforcer.get_filtered_named_policy("p", 0, role)

    # Remove duplicates
    resources = set([policy[1] for policy in role_policies])

    permissions_per_resource = []
    for resource in resources:
        # Group actions per resource
        resource_permissions = filter(
            lambda permission: permission[1] == resource, role_policies
        )

        # Extract actions
        actions = [permission[2] for permission in resource_permissions]
        permissions_per_resource.append({"resource": resource, "actions": actions})

    return permissions_per_resource
