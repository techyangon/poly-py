import argparse
import asyncio
from typing import AsyncIterator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from poly.config import Settings, get_settings
from poly.rbac.models import get_enforcer
from poly.services.resources import get_all_resources


async def get_session(
    settings: Settings = get_settings(),
) -> AsyncIterator[AsyncSession]:  # pragma: no cover
    uri = (
        f"postgresql+asyncpg://"
        f"{settings.db_username}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/"
        f"{settings.db_name}"
    )

    engine = create_async_engine("".join(uri), echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session, session.begin():
        yield session

    await engine.dispose()


async def upgrade(settings: Settings = get_settings()):
    permissions = ["delete", "post", "put", "read"]
    resources = []

    async for session in get_session():
        resources = await get_all_resources(session=session)

    if not resources:
        raise SystemExit()

    policies = [
        ["role_admin", resource.name, permission]
        for resource in resources
        for permission in permissions
    ]

    enforcer = await get_enforcer()

    await enforcer.add_named_policies("p", policies)
    await enforcer.add_role_for_user(settings.admin_username, "role_admin")


async def downgrade(settings: Settings = get_settings()):
    uri = (
        f"postgresql+asyncpg://"
        f"{settings.db_username}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/"
        f"{settings.db_name}"
    )

    engine = create_async_engine("".join(uri), echo=True)

    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE casbin_rule;"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed roles and permissions")
    parser.add_argument("--type")
    args = parser.parse_args()

    if args.type == "upgrade":
        asyncio.run(upgrade())
    elif args.type == "downgrade":
        asyncio.run(downgrade())
