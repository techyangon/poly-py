from typing import Annotated

from fastapi import Depends, FastAPI

from poly import __version__
from poly.routers import auth, branches, locations, permissions, resources, roles, user
from poly.services.auth import validate_access_token

app = FastAPI()
app.include_router(auth.router)
app.include_router(branches.router)
app.include_router(locations.router)
app.include_router(permissions.router)
app.include_router(resources.router)
app.include_router(roles.router)
app.include_router(user.router)


@app.get("/")
async def root(_: Annotated[str, Depends(validate_access_token)]):
    return {"message": "Welcome to Poly"}


@app.get("/version")
async def version():
    return {"message": __version__}
