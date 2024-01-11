from casbin import AsyncEnforcer, Model
from casbin_async_sqlalchemy_adapter import Adapter
from sqlalchemy.ext.asyncio import create_async_engine

from poly.config import get_settings, rbac_models


async def get_enforcer():  # pragma: no cover
    settings = get_settings()
    uri = (
        f"postgresql+asyncpg://"
        f"{settings.db_username}:{settings.db_password}@"
        f"{settings.db_host}:{settings.db_port}/"
        f"{settings.db_name}"
    )
    engine = create_async_engine("".join(uri), echo=True)

    adapter = Adapter(engine=engine)
    await adapter.create_table()

    model = Model()
    model.load_model_from_text(text=rbac_models)

    enforcer = AsyncEnforcer(model=model)
    enforcer.set_adapter(adapter)
    await enforcer.load_policy()

    await engine.dispose()

    return enforcer
