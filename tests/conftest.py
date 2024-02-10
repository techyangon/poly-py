from contextlib import asynccontextmanager
from typing import Annotated

import pytest_asyncio
from asgi_lifespan import LifespanManager
from fastapi import Depends, FastAPI, HTTPException, status
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from poly.config import Settings, get_settings
from poly.db.models import Base, Branch, City, Resource, Role, State, Township, User
from poly.main import create_app
from poly.rbac.models import get_enforcer
from poly.services import oauth2_scheme
from poly.services.auth import get_active_user, password_context, validate_access_token


def override_get_settings() -> Settings:
    return Settings(
        _env_file=".env.development", _env_file_encoding="utf-8"  # pyright: ignore
    )


@asynccontextmanager
async def override_lifespan(app: FastAPI):
    settings = override_get_settings()
    uri = (
        f"postgresql+asyncpg://"
        f"{settings.db_username}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/"
        f"{settings.db_name}"
    )
    engine = create_async_engine("".join(uri), echo=True, echo_pool="debug")

    app.state.engine = engine
    app.state.async_session = async_sessionmaker(engine, expire_on_commit=False)

    yield

    await engine.dispose()


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
async def db_engine(settings):
    settings = override_get_settings()
    uri = (
        f"postgresql+asyncpg://"
        f"{settings.db_username}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/"
        f"{settings.db_name}"
    )
    engine = create_async_engine("".join(uri), echo=True, echo_pool="debug")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.execute(text("SET session_replication_role = 'replica';"))

        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
            await conn.execute(text(f"ALTER SEQUENCE {table.name}_id_seq RESTART;"))

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def db_session(db_engine):
    yield async_sessionmaker(db_engine, expire_on_commit=False)


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
    resources = ["branches", "roles"]

    policies = [
        ["role_admin", resource, permission]
        for resource in resources
        for permission in permissions
    ]
    policies.append(["role_admin", "locations", "GET"])
    policies.append(["role_admin", "resources", "GET"])

    enforcer = await get_enforcer(settings=settings)

    await enforcer.add_named_policies("p", policies)
    await enforcer.add_role_for_user(settings.admin_username, "role_admin")


@pytest_asyncio.fixture(scope="session")
async def client():
    app = create_app(lifespan=override_lifespan)
    async with LifespanManager(app=app) as manager:
        async with AsyncClient(
            app=manager.app, base_url="http://localhost/"
        ) as async_client:
            app.dependency_overrides[get_settings] = override_get_settings
            app.dependency_overrides[validate_access_token] = (
                override_validate_access_token
            )
            yield async_client
            app.dependency_overrides = {}
