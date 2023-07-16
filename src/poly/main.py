from fastapi import Depends, FastAPI

from poly.routers import resources, roles
from poly.services.auth import get_current_auth_user

app = FastAPI()
app.include_router(resources.router)
app.include_router(roles.router)


@app.get("/")
async def root(user=Depends(get_current_auth_user)):
    return {"message": "Welcome to Poly"}


@app.get("/version")
async def version():
    return {"message": "Poly 0.1.0"}
