import os
os.environ["ADMIN_API_KEY"] = "secret-admin-key"
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import engine, Base, SessionLocal
from app.dependencies import get_db



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

@pytest_asyncio.fixture(autouse=True)
def mock_prediction_service(monkeypatch):
    import app.api.v1.predictions as predictions_api
    class MockModel:
        classes_ = ["billing", "technical_support", "refund", "account_management"]
        def predict(self, X):
            return ["billing"]
        def predict_proba(self, X):
            return [[0.1, 0.2, 0.7, 0.0]]
    class MockService:
        model = MockModel()
        metadata = {"model_version": "v1.0"}
        def predict(self, text):
            return "refund", 0.9, "v1.0"
    monkeypatch.setattr(predictions_api, "prediction_service", MockService())
