from fastapi import Depends, FastAPI

from poly.routers import auth, resources, roles
from poly.services.auth import get_user_from_token

app = FastAPI()
app.include_router(auth.router)
app.include_router(resources.router)
app.include_router(roles.router)


@app.get("/")
async def root(user=Depends(get_user_from_token)):
    return {"message": "Welcome to Poly"}


@app.get("/version")
async def version():
    return {"message": "Poly 0.1.0"}
