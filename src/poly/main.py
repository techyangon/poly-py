from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from poly import __version__
from poly.config import get_settings
from poly.routers import auth, branches, locations, permissions, resources, roles, user
from poly.services.auth import validate_access_token

router = APIRouter(tags=["root"])


@router.get("/")
async def root(_: Annotated[str, Depends(validate_access_token)]):
    return {"message": "Welcome to Poly"}


@router.get("/version")
async def version():
    return {"message": __version__}


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
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


def create_app(lifespan):
    app = FastAPI(lifespan=lifespan)

    app.include_router(auth.router)
    app.include_router(branches.router)
    app.include_router(locations.router)
    app.include_router(permissions.router)
    app.include_router(resources.router)
    app.include_router(roles.router)
    app.include_router(router)
    app.include_router(user.router)

    return app


app = create_app(lifespan=lifespan)
