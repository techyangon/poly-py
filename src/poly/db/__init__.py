from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime

from poly.config import Settings, get_settings


# https://docs.sqlalchemy.org/en/20/core/compiler.html#utc-timestamp-function
class UTCNow(expression.FunctionElement):
    type: DateTime = DateTime()  # type: ignore
    inherit_cache = True


@compiles(UTCNow, "postgresql")
def pg_utcnow(element, compiler, **kw):  # pragma: no cover
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


@asynccontextmanager
async def get_engine(settings: Settings) -> AsyncIterator[AsyncEngine]:
    uri = (
        f"postgresql+asyncpg://"
        f"{settings.db_username}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/"
        f"{settings.db_name}"
    )
    engine = create_async_engine("".join(uri), echo=True)

    yield engine

    await engine.dispose()


async def get_session(
    settings: Settings = Depends(get_settings),
) -> async_sessionmaker:  # pragma: no cover
    async with get_engine(settings=settings) as engine:
        return async_sessionmaker(engine, expire_on_commit=False)
