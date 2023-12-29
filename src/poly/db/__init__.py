from typing import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression
from sqlalchemy.types import DateTime

from poly.config import Settings, get_settings


# https://docs.sqlalchemy.org/en/20/core/compiler.html#utc-timestamp-function
class UTCNow(expression.FunctionElement):
    type: DateTime = DateTime()
    inherit_cache = True


@compiles(UTCNow, "postgresql")
def pg_utcnow(element, compiler, **kw):  # pragma: no cover
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"


async def get_session(
    settings: Settings = Depends(get_settings),
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
