import secrets
from app.db.session import SessionLocal
from fastapi import Header, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from typing import Optional
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token", auto_error=False)

async def get_db():
    async with SessionLocal() as db:
        yield db

def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
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

def get_admin_api_key(x_api_key: Optional[str] = Header(None)):
    if not x_api_key or not secrets.compare_digest(x_api_key, settings.ADMIN_API_KEY):
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

def get_current_admin_or_api_key(
    x_api_key: Optional[str] = Header(None),
    token: Optional[str] = Depends(oauth2_scheme)
):
    if x_api_key and secrets.compare_digest(x_api_key, settings.ADMIN_API_KEY):
        return {"role": "ADMIN", "username": "api_key_admin"}
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_current_user(token)
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Requires ADMIN role")
    return user

def get_current_reviewer_or_api_key(
    x_api_key: Optional[str] = Header(None),
    token: Optional[str] = Depends(oauth2_scheme)
):
    if x_api_key and secrets.compare_digest(x_api_key, settings.ADMIN_API_KEY):
        return {"role": "ADMIN", "username": "api_key_admin"}
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_current_user(token)
    if user["role"] not in ["REVIEWER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Requires REVIEWER or ADMIN role")
    return user
