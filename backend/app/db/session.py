from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
from sqlalchemy import pool

uri = settings.SQLALCHEMY_DATABASE_URI
uri = uri.replace('sslmode=require', 'ssl=require')
if uri.startswith('postgresql+psycopg2://'):
    uri = uri.replace('postgresql+psycopg2://', 'postgresql+asyncpg://')
elif uri.startswith('sqlite:///'):
    uri = uri.replace('sqlite:///', 'sqlite+aiosqlite:///')
elif uri.startswith('postgresql://'):
    uri = uri.replace('postgresql://', 'postgresql+asyncpg://')

engine = create_async_engine(
    uri,
    pool_pre_ping=True,
    
    
    poolclass=pool.NullPool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
