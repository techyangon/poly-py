import asyncio
import os
from typing import Annotated, AsyncIterator, Mapping

import pytest_asyncio
from fastapi import Depends, Header, HTTPException, status
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from poly.config import Settings, get_settings
from poly.db import get_session
from poly.db.models import Base, Resource, Role, User
from poly.main import app
from poly.services import oauth2_scheme
from poly.services.auth import password_context, validate_token


def override_get_settings() -> Settings:
    return Settings(
        access_token_audience=os.getenv("ACCESS_TOKEN_AUDIENCE", "http://localhost"),
        access_token_issuer=os.getenv("ACCESS_TOKEN_ISSUER", "http://localhost"),
        admin_mail=os.getenv("ADMIN_MAIL", "admin@mail.com"),
        admin_password=os.getenv("ADMIN_PASSWORD", "passwd"),
        admin_username=os.getenv("ADMIN_USERNAME", "admin"),
        db_host=os.getenv("DB_HOST", "postgres"),
        db_name=os.getenv("DB_NAME", "test_poly"),
        db_password=os.getenv("DB_PASSWORD", "passwd"),
        db_port=os.getenv("DB_PASSWORD", "5432"),
        db_username=os.getenv("DB_USERNAME", "postgres"),
        secret_key=os.getenv("SECRET_KEY", "secret"),
    )


async def override_get_session(
    settings=Depends(get_settings),
) -> AsyncIterator[AsyncSession]:
    settings = override_get_settings()
    uri = (
        f"postgresql+asyncpg://"
        f"{settings.db_username}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/"
        f"{settings.db_name}"
    )

    engine = create_async_engine("".join(uri), echo=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session


def override_validate_token(
    x_username: Annotated[str, Header()],
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Settings = Depends(get_settings),
) -> Mapping:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Empty token"
        )
    return {"sub": x_username}


@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    event_loop_policy = asyncio.get_event_loop_policy()
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
def settings():
    return override_get_settings()


@pytest_asyncio.fixture(scope="module", autouse=True)
async def engine(settings):
    uri = (
        f"postgresql+asyncpg://"
        f"{settings.db_username}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/"
        f"{settings.db_name}"
    )
    engine = create_async_engine("".join(uri), echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.execute(text("SET session_replication_role = 'replica';"))

        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
            await conn.execute(text(f"ALTER SEQUENCE {table.name}_id_seq RESTART;"))


@pytest_asyncio.fixture(scope="module")
async def session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="module")
async def resources(session):
    async with session.begin():
        role = Resource(name="role", created_by="system", updated_by="system")
        staff = Resource(name="staff", created_by="system", updated_by="system")
        session.add_all([role, staff])

    async with session.begin():
        query = select(Resource).order_by(Resource.created_at)
        result = await session.scalars(query)
        return result.all()


@pytest_asyncio.fixture(scope="module")
async def roles(session):
    async with session.begin():
        admin = Role(name="admin", created_by="system", updated_by="system")
        staff = Role(name="staff", created_by="system", updated_by="system")
        session.add_all([admin, staff])

    async with session.begin():
        query = select(Role).order_by(Role.created_at)
        result = await session.scalars(query)
        return result.all()


@pytest_asyncio.fixture(scope="module")
async def user(session):
    async with session.begin():
        user = User(
            name="user",
            email="user@mail.com",
            password=password_context.hash("passwd"),
            is_active=True,
            created_by="system",
            updated_by="system",
        )
        session.add(user)

    async with session.begin():
        query = select(User).where(User.email == "user@mail.com")
        result = await session.scalars(query)
        return result.one()


@pytest_asyncio.fixture(scope="module")
async def inactive_user(session):
    async with session.begin():
        user = User(
            name="user.inactive",
            email="user-inactive@mail.com",
            password=password_context.hash("passwd"),
            is_active=False,
            created_by="system",
            updated_by="system",
        )
        session.add(user)

    async with session.begin():
        query = select(User).where(User.email == "user-inactive@mail.com")
        result = await session.scalars(query)
        return result.one()


@pytest_asyncio.fixture()
async def client():
    async with AsyncClient(app=app, base_url="http://poly.test/") as client:
        app.dependency_overrides[get_settings] = override_get_settings
        app.dependency_overrides[get_session] = override_get_session
        app.dependency_overrides[validate_token] = override_validate_token
        yield client
        app.dependency_overrides = {}
