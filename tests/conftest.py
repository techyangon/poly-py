from typing import Annotated

import pytest_asyncio
from fastapi import Depends, HTTPException, status
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.config import Settings, get_settings
from poly.db import get_engine
from poly.db.models import Base, Branch, City, Resource, Role, State, Township, User
from poly.main import app
from poly.rbac.models import get_enforcer
from poly.services import oauth2_scheme
from poly.services.auth import get_active_user, password_context, validate_access_token


def override_get_settings() -> Settings:
    return Settings(
        _env_file=".env.development", _env_file_encoding="utf-8"  # pyright: ignore
    )


async def override_validate_access_token(
    settings: Annotated[Settings, Depends(get_settings)],
    token: Annotated[str, Depends(oauth2_scheme)],
    user: Annotated[User, Depends(get_active_user)],
) -> str:  # pragma: no cover
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty token",
        )
    return user.name


@pytest_asyncio.fixture(scope="session")
def settings():
    return Settings(
        _env_file=".env.development", _env_file_encoding="utf-8"  # pyright: ignore
    )


@pytest_asyncio.fixture(scope="session")
async def db_session(settings):
    async with get_engine(settings=settings) as engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield async_sessionmaker(engine, expire_on_commit=False)

        async with engine.begin() as conn:
            await conn.execute(text("SET session_replication_role = 'replica';"))

            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())
                await conn.execute(text(f"ALTER SEQUENCE {table.name}_id_seq RESTART;"))


@pytest_asyncio.fixture(scope="session")
async def resources(db_session):
    async with db_session() as session, session.begin():
        session.add_all(
            [
                Resource(name="role", created_by="system", updated_by="system"),
                Resource(name="staff", created_by="system", updated_by="system"),
            ]
        )

    async with db_session() as session, session.begin():
        result = await session.scalars(select(Resource).order_by(Resource.created_at))
        yield result.all()


@pytest_asyncio.fixture(scope="session")
async def roles(db_session):
    async with db_session() as session, session.begin():
        session.add_all(
            [
                Role(name="admin", created_by="system", updated_by="system"),
                Role(name="staff", created_by="system", updated_by="system"),
            ]
        )

    async with db_session() as session, session.begin():
        result = await session.scalars(select(Role).order_by(Role.created_at))
        yield result.all()


@pytest_asyncio.fixture(scope="session")
async def user(db_session, settings):
    async with db_session() as session, session.begin():
        session.add(
            User(
                name=settings.admin_username,
                email=settings.admin_mail,
                password=password_context.hash("passwd"),
                is_active=True,
                created_by="system",
                updated_by="system",
            )
        )

    async with db_session() as session, session.begin():
        result = await session.scalars(
            select(User).where(User.email == settings.admin_mail)
        )
        yield result.one()


@pytest_asyncio.fixture(scope="session")
async def inactive_user(db_session):
    async with db_session() as session, session.begin():
        session.add(
            User(
                name="user.inactive",
                email="user-inactive@mail.com",
                password=password_context.hash("passwd"),
                is_active=False,
                created_by="system",
                updated_by="system",
            )
        )

    async with db_session() as session, session.begin():
        result = await session.scalars(
            select(User).where(User.email == "user-inactive@mail.com")
        )
        yield result.one()


@pytest_asyncio.fixture(scope="session")
async def unauthorized_user(db_session):
    async with db_session() as session, session.begin():
        session.add(
            User(
                name="user.unauthorized",
                email="user-unauthorized@mail.com",
                password=password_context.hash("passwd"),
                is_active=True,
                created_by="system",
                updated_by="system",
            )
        )

    async with db_session() as session, session.begin():
        result = await session.scalars(
            select(User).where(User.email == "user-unauthorized@mail.com")
        )
        yield result.one()


@pytest_asyncio.fixture(scope="session")
async def state(db_session):
    async with db_session() as session, session.begin():
        session.add(
            State(
                name="state1",
                created_by="system",
                updated_by="system",
            )
        )

    async with db_session() as session, session.begin():
        result = await session.scalars(select(State).where(State.name == "state1"))
        yield result.one()


@pytest_asyncio.fixture(scope="session")
async def city(db_session, state):
    async with db_session() as session, session.begin():
        session.add(
            City(
                name="city1",
                state_id=state.id,
                created_by="system",
                updated_by="system",
            )
        )

    async with db_session() as session, session.begin():
        result = await session.scalars(select(City).where(City.name == "city1"))
        yield result.one()


@pytest_asyncio.fixture(scope="session")
async def township(city, db_session):
    async with db_session() as session, session.begin():
        session.add(
            Township(
                name="township1",
                city_id=city.id,
                created_by="system",
                updated_by="system",
            )
        )

    async with db_session() as session, session.begin():
        result = await session.scalars(
            select(Township).where(Township.name == "township1")
        )
        yield result.one()


@pytest_asyncio.fixture(scope="session")
async def branches(db_session, township, settings):
    async with db_session() as session, session.begin():
        session.add_all(
            [
                Branch(
                    name="branch1",
                    address="address1",
                    township_id=township.id,
                    created_by=settings.admin_username,
                    updated_by=settings.admin_username,
                ),
                Branch(
                    name="branch2",
                    address="address2",
                    township_id=township.id,
                    created_by=settings.admin_username,
                    updated_by=settings.admin_username,
                ),
            ]
        )

    async with db_session() as session, session.begin():
        result = await session.scalars(select(Branch).order_by(Branch.created_at))
        yield result.all()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def permissions(settings):
    permissions = ["DELETE", "GET", "POST", "PUT"]
    resources = ["branches", "locations", "resources", "roles"]

    policies = [
        ["role_admin", resource, permission]
        for resource in resources
        for permission in permissions
    ]

    enforcer = await get_enforcer(settings=settings)

    await enforcer.add_named_policies("p", policies)
    await enforcer.add_role_for_user(settings.admin_username, "role_admin")


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://localhost/") as client:
        app.dependency_overrides[get_settings] = override_get_settings
        app.dependency_overrides[validate_access_token] = override_validate_access_token
        yield client
        app.dependency_overrides = {}
