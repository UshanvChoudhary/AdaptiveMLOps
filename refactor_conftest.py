import os

conftest_code = """import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import engine, Base, SessionLocal
from app.dependencies import get_db

os.environ["ADMIN_API_KEY"] = "secret-admin-key"

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def async_db():
    async with SessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(async_db):
    app.dependency_overrides[get_db] = lambda: async_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
"""

with open('backend/tests/conftest.py', 'w', encoding='utf-8') as f:
    f.write(conftest_code)
