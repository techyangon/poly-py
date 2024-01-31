import argparse
import asyncio

from sqlalchemy import text

from poly.config import Settings, get_settings
from poly.db import get_engine, get_session
from poly.rbac.models import get_enforcer
from poly.services.resources import get_all_resources


async def upgrade(settings: Settings):
    permissions = ["DELETE", "GET", "POST", "PUT"]
    resources = []

    async_session = await get_session(settings=settings)
    resources = await get_all_resources(async_session=async_session)

    if not resources:
        raise SystemExit()

    policies = [
        ["role_admin", resource.name, permission]
        for resource in resources
        for permission in permissions
    ]
    policies.append(["role_admin", "locations", "GET"])
    policies.append(["role_admin", "resources", "GET"])

    enforcer = await get_enforcer(settings=settings)

    await enforcer.add_named_policies("p", policies)
    await enforcer.add_role_for_user(settings.admin_username, "role_admin")


async def downgrade(settings: Settings):
    async with get_engine(settings=settings) as engine, engine.begin() as conn:
        await conn.execute(text("DROP TABLE casbin_rule;"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed roles and permissions")
    parser.add_argument("--type")
    args = parser.parse_args()

    settings = get_settings()

    if args.type == "upgrade":
        asyncio.run(upgrade(settings=settings))
    elif args.type == "downgrade":
        asyncio.run(downgrade(settings=settings))
