from typing import Annotated

import pytest_asyncio
from fastapi import Depends, HTTPException, status
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker

from poly.config import Settings, get_settings
from poly.db import get_engine
from poly.db.models import Base, Resource, Role, User
from poly.main import app
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
    return "user"


@pytest_asyncio.fixture(scope="session", autouse=True)
def settings():
    return Settings(
        _env_file=".env.development", _env_file_encoding="utf-8"  # pyright: ignore
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
async def db_session(settings):
    async with get_engine(settings=settings) as engine, engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        yield async_sessionmaker(engine, expire_on_commit=False)

        await conn.execute(text("SET session_replication_role = 'replica';"))

        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
            await conn.execute(text(f"ALTER SEQUENCE {table.name}_id_seq RESTART;"))


@pytest_asyncio.fixture(scope="session", autouse=True)
async def resources(db_session):
    async with db_session() as session, session.begin():
        role = Resource(name="role", created_by="system", updated_by="system")
        staff = Resource(name="staff", created_by="system", updated_by="system")
        session.add_all([role, staff])

    async with db_session() as session, session.begin():
        query = select(Resource).order_by(Resource.created_at)
        result = await session.scalars(query)
        yield result.all()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def roles(db_session):
    async with db_session() as session, session.begin():
        admin = Role(name="admin", created_by="system", updated_by="system")
        staff = Role(name="staff", created_by="system", updated_by="system")
        session.add_all([admin, staff])

    async with db_session() as session, session.begin():
        query = select(Role).order_by(Role.created_at)
        result = await session.scalars(query)
        yield result.all()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def user(db_session):
    async with db_session() as session, session.begin():
        user = User(
            name="user",
            email="user@mail.com",
            password=password_context.hash("passwd"),
            is_active=True,
            created_by="system",
            updated_by="system",
        )
        session.add(user)

    async with db_session() as session, session.begin():
        query = select(User).where(User.email == "user@mail.com")
        result = await session.scalars(query)
        yield result.one()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def inactive_user(db_session):
    async with db_session() as session, session.begin():
        user = User(
            name="user.inactive",
            email="user-inactive@mail.com",
            password=password_context.hash("passwd"),
            is_active=False,
            created_by="system",
            updated_by="system",
        )
        session.add(user)

    async with db_session() as session, session.begin():
        query = select(User).where(User.email == "user-inactive@mail.com")
        result = await session.scalars(query)
        yield result.one()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def client():
    async with AsyncClient(app=app, base_url="http://localhost/") as client:
        app.dependency_overrides[get_settings] = override_get_settings
        app.dependency_overrides[validate_access_token] = override_validate_access_token
        yield client
        app.dependency_overrides = {}
