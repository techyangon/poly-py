from typing import Annotated

from casbin import AsyncEnforcer, Model
from casbin_async_sqlalchemy_adapter import Adapter
from fastapi import Depends

from poly.config import Settings, get_rbac_models, get_settings
from poly.db import get_engine


async def get_enforcer(
    settings: Annotated[Settings, Depends(get_settings)]
):  # pragma: no cover
    model = Model()
    model.load_model_from_text(text=get_rbac_models())

    enforcer = AsyncEnforcer(model=model)

    async with get_engine(settings=settings) as engine:
        adapter = Adapter(engine=engine)
        await adapter.create_table()

        enforcer.set_adapter(adapter)
        await enforcer.load_policy()

    return enforcer
