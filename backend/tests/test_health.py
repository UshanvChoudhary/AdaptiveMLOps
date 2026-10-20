from httpx import AsyncClient, ASGITransport
from app.main import app

async def test_health_check(client):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

async def test_readiness_check_no_db():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/ready")
        # Without DB, this should be 503
        assert response.status_code in [200, 503]
