import secrets
from app.db.session import SessionLocal
from fastapi import Header, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from typing import Optional
from jose import JWTError, jwt
import asyncio

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

async def get_db():
    async with SessionLocal() as db:
        yield db

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        role: str = payload.get("role")
        if role is None:
            raise credentials_exception
        return {"role": role, "username": payload.get("sub")}
    except JWTError:
        raise credentials_exception

def get_current_reviewer(user: dict = Depends(get_current_user)):
    if user["role"] not in ["REVIEWER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Requires REVIEWER or ADMIN role")
    return user

def get_current_admin(user: dict = Depends(get_current_user)):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Requires ADMIN role")
    return user

def get_admin_api_key(x_api_key: str = Header(None)):
    if not x_api_key or not secrets.compare_digest(x_api_key, settings.ADMIN_API_KEY):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key
