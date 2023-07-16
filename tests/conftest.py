import asyncio
import os

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from poly.config import Settings, get_settings
from poly.db.models import Base, Resource
from poly.main import app


def override_get_settings() -> Settings:
    return Settings(
        db_host=os.getenv("DB_HOST", "postgres"),
        db_name=os.getenv("DB_NAME", "test_poly"),
        db_username=os.getenv("DB_USERNAME", "postgres"),
        db_password=os.getenv("DB_PASSWORD", "passwd"),
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    event_loop_policy = asyncio.get_event_loop_policy()
    loop = event_loop_policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
def settings():
    return Settings(
        db_host=os.getenv("DB_HOST", "postgres"),
        db_name=os.getenv("DB_NAME", "test_poly"),
        db_username=os.getenv("DB_USERNAME", "postgres"),
        db_password=os.getenv("DB_PASSWORD", "passwd"),
    )


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
        role = Resource(name="role", created_by="admin", updated_by="admin")
        staff = Resource(name="staff", created_by="admin", updated_by="admin")
        session.add_all([role, staff])

    query = select(Resource).order_by(Resource.created_at)
    resources = await session.scalars(query)
    yield resources.all()


@pytest_asyncio.fixture()
async def client():
    async with AsyncClient(app=app, base_url="http://poly.test/") as client:
        app.dependency_overrides[get_settings] = override_get_settings
        yield client
        app.dependency_overrides = {}
