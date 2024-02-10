from casbin import AsyncEnforcer, Model
from casbin_async_sqlalchemy_adapter import Adapter
from sqlalchemy.ext.asyncio import AsyncEngine

from poly.config import get_rbac_models


async def get_enforcer(engine: AsyncEngine):  # pragma: no cover
    model = Model()
    model.load_model_from_text(text=get_rbac_models())

    enforcer = AsyncEnforcer(model=model)

    adapter = Adapter(engine=engine, warning=False)
    await adapter.create_table()

    enforcer.set_adapter(adapter)
    await enforcer.load_policy()

    return enforcer
