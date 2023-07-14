from fastapi import Depends, FastAPI

from poly.services.auth import get_current_auth_user

app = FastAPI()


@app.get("/")
async def root(user=Depends(get_current_auth_user)):
    return {"message": "Welcome to Poly"}


@app.get("/version")
async def version():
    return {"message": "Poly 0.1.0"}
