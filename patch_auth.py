import os

auth_code = """from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.config import settings
from datetime import datetime, timedelta
from jose import jwt

router = APIRouter()

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Hardcoded dummy users for demonstration
    users = {
        "admin": {"password": "password", "role": "ADMIN"},
        "reviewer": {"password": "password", "role": "REVIEWER"},
        "user": {"password": "password", "role": "USER"},
    }
    
    user = users.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username, "role": user["role"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}
"""
with open("backend/app/api/v1/auth.py", "w") as f:
    f.write(auth_code)

deps_code = """from app.db.session import SessionLocal
from fastapi import Header, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from typing import Optional
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    # Fallback for internal services
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key
"""
with open("backend/app/dependencies.py", "w") as f:
    f.write(deps_code)
