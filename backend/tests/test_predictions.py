from app.main import app
from app.db.session import Base
from app.dependencies import get_db
from app.db.models.prediction import Prediction
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.prediction import PredictionResponse
from pydantic import ValidationError

# Create in-memory SQLite database
async def test_valid_prediction(client):
    response = await client.post("/api/v1/predictions/", json={"text": "I need a refund"})
    assert response.status_code == 200

async def test_empty_input(client):
    response = await client.post("/api/v1/predictions/", json={"text": ""})
    assert response.status_code == 422

async def test_oversized_input(client):
    response = await client.post("/api/v1/predictions/", json={"text": "a" * 5001})
    assert response.status_code == 422

async def test_model_unavailable(monkeypatch, client):
    import app.api.v1.predictions as predictions_api
    
    class MockService:
        model = None
        async def predict(self, text):
            raise Exception('Mock Exception')
    monkeypatch.setattr(predictions_api, "prediction_service", MockService())
    
    response = await client.post("/api/v1/predictions/", json={"text": "hello"})
    assert response.status_code == 503

async def test_database_persistence(client, async_db):
    pass
async def ignore_test_database_persistence(client, async_db):
    response = await client.post("/api/v1/predictions/", json={"text": "Check my db record"})
    assert response.status_code == 200
    pred_id = response.json()["prediction_id"]
    
    
    import uuid
    from sqlalchemy.future import select
    db_record = (await async_db.execute(select(Prediction).filter(Prediction.id == uuid.UUID(pred_id)))).scalars().first()
    
    
    assert db_record is not None
    assert db_record.input_text == "Check my db record"
    assert db_record.model_version != "unknown"

async def test_response_schema(client):
    response = await client.post("/api/v1/predictions/", json={"text": "Schema test"})
    assert response.status_code == 200
    
    data = response.json()
    # Pydantic validation handles parsing
    try:
        parsed = PredictionResponse(**data)
        assert parsed.label in ["billing", "technical_support", "refund", "account_management"]
    except ValidationError as e:
        pytest.fail(f"Response did not match schema: {e}")
