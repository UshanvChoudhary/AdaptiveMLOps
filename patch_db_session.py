import os

with open('backend/app/config.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('postgresql+psycopg2://', 'postgresql+asyncpg://')
content = content.replace('sqlite:///', 'sqlite+aiosqlite:///')

with open('backend/app/config.py', 'w', encoding='utf-8') as f:
    f.write(content)

session_code = """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', 'sqlite+aiosqlite:///'),
    pool_pre_ping=True,
    pool_size=10 if 'sqlite' not in settings.SQLALCHEMY_DATABASE_URI else 5,
    max_overflow=20 if 'sqlite' not in settings.SQLALCHEMY_DATABASE_URI else 10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
Base = declarative_base()
"""
with open('backend/app/db/session.py', 'w', encoding='utf-8') as f:
    f.write(session_code)

