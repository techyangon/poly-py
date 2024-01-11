import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from poly.config import Settings, get_settings
from poly.db.models import Base, Resource, Role, User
from poly.main import app
from poly.services.auth import password_context


def override_get_settings() -> Settings:
    return Settings(
        _env_file=".env.development", _env_file_encoding="utf-8"  # pyright: ignore
    )


@pytest_asyncio.fixture(scope="session")
def settings():
    return Settings(
        _env_file=".env.development", _env_file_encoding="utf-8"  # pyright: ignore
    )


@pytest_asyncio.fixture(scope="session")
async def db_session(settings):
    uri = (
        f"postgresql+asyncpg://"
        f"{settings.db_username}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/"
        f"{settings.db_name}"
    )
    engine = create_async_engine("".join(uri), echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.execute(text("SET session_replication_role = 'replica';"))

        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
            await conn.execute(text(f"ALTER SEQUENCE {table.name}_id_seq RESTART;"))

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def resources(db_session):
    async with db_session() as session, session.begin():
        role = Resource(name="role", created_by="system", updated_by="system")
        staff = Resource(name="staff", created_by="system", updated_by="system")
        session.add_all([role, staff])

    async with db_session() as session, session.begin():
        query = select(Resource).order_by(Resource.created_at)
        result = await session.scalars(query)
        yield result.all()


@pytest_asyncio.fixture(scope="session")
async def roles(db_session):
    async with db_session() as session, session.begin():
        admin = Role(name="admin", created_by="system", updated_by="system")
        staff = Role(name="staff", created_by="system", updated_by="system")
        session.add_all([admin, staff])

    async with db_session() as session, session.begin():
        query = select(Role).order_by(Role.created_at)
        result = await session.scalars(query)
        yield result.all()


@pytest_asyncio.fixture(scope="session")
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


@pytest_asyncio.fixture(scope="session")
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


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://localhost/") as client:
        app.dependency_overrides[get_settings] = override_get_settings
        yield client
        app.dependency_overrides = {}
