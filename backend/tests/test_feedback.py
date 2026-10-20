import pytest
import uuid
from app.main import app
from app.db.session import Base
from app.dependencies import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models.prediction import Prediction
from app.db.models.feedback import Feedback

@pytest.fixture
async def test_prediction(client):

    response = await client.post("/api/v1/predictions/", json={"text": "Hello world"})
    assert response.status_code == 200
    return response.json()

async def test_valid_feedback_correct(client, test_prediction):
    pred_id = test_prediction["prediction_id"]
    response = await client.post(f"/api/v1/predictions/{pred_id}/feedback", json={
        "is_correct": True
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is True
    assert data["prediction_id"] == pred_id
    assert data["feedback_status"] == "pending"

async def test_valid_feedback_incorrect(client):
    pred = (await client.post("/api/v1/predictions/", json={"text": "New request"})).json()
    pred_id = pred["prediction_id"]
    
    response = await client.post(f"/api/v1/predictions/{pred_id}/feedback", json={
        "is_correct": False,
        "corrected_label": "billing",
        "comments": "Should be billing"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] is False
    assert data["corrected_label"] == "billing"

async def test_missing_corrected_label(client):
    pred = (await client.post("/api/v1/predictions/", json={"text": "Bad request"})).json()
    pred_id = pred["prediction_id"]
    
    response = await client.post(f"/api/v1/predictions/{pred_id}/feedback", json={
        "is_correct": False
    })
    assert response.status_code == 422

async def test_invalid_corrected_label(client):
    pred = (await client.post("/api/v1/predictions/", json={"text": "Another bad request"})).json()
    pred_id = pred["prediction_id"]
    
    response = await client.post(f"/api/v1/predictions/{pred_id}/feedback", json={
        "is_correct": False,
        "corrected_label": "invalid_category"
    })
    assert response.status_code == 422

async def test_duplicate_feedback(client, test_prediction):
    pred_id = test_prediction["prediction_id"]
    
    res1 = await client.post(f"/api/v1/predictions/{pred_id}/feedback", json={
        "is_correct": True
    })
    assert res1.status_code == 200
    
    res2 = await client.post(f"/api/v1/predictions/{pred_id}/feedback", json={
        "is_correct": True
    })
    assert res2.status_code == 409

async def test_get_feedback(client, test_prediction):
    res = await client.get("/api/v1/feedback/me")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
