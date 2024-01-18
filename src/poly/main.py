from fastapi import Depends, FastAPI

from poly.routers import auth, branches, locations, resources, roles
from poly.services.auth import validate_access_token

app = FastAPI()
app.include_router(auth.router)
app.include_router(branches.router)
app.include_router(locations.router)
app.include_router(resources.router)
app.include_router(roles.router)


@app.get("/")
async def root(user=Depends(validate_access_token)):
    return {"message": "Welcome to Poly"}


@app.get("/version")
async def version():
    return {"message": "Poly 0.1.0"}
