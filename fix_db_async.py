import os

# Fix config.py to not have asyncpg by default
with open('backend/app/config.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('postgresql+asyncpg://', 'postgresql+psycopg2://')
content = content.replace('sqlite+aiosqlite:///', 'sqlite:///')

with open('backend/app/config.py', 'w', encoding='utf-8') as f:
    f.write(content)

# Fix dependencies.py to have async get_db
deps = """from app.db.session import SessionLocal
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
    if x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key
"""
with open("backend/app/dependencies.py", "w") as f:
    f.write(deps)

# Fix session.py to convert URI for async
session_code = """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings
from sqlalchemy import pool

uri = settings.SQLALCHEMY_DATABASE_URI
if uri.startswith('postgresql+psycopg2://'):
    uri = uri.replace('postgresql+psycopg2://', 'postgresql+asyncpg://')
elif uri.startswith('sqlite:///'):
    uri = uri.replace('sqlite:///', 'sqlite+aiosqlite:///')
elif uri.startswith('postgresql://'):
    uri = uri.replace('postgresql://', 'postgresql+asyncpg://')

engine = create_async_engine(
    uri,
    pool_pre_ping=True,
    pool_size=10 if 'sqlite' not in uri else 5,
    max_overflow=20 if 'sqlite' not in uri else 10,
    poolclass=pool.NullPool if 'sqlite' in uri else pool.QueuePool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()
"""
with open('backend/app/db/session.py', 'w', encoding='utf-8') as f:
    f.write(session_code)

