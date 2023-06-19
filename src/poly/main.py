from fastapi import Depends, FastAPI
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI()


@app.get("/")
async def root(token: str = Depends(oauth2_scheme)):
    return {"message": "Welcome to Poly"}
