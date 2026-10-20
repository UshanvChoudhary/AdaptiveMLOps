import pytest
import requests
import uuid
import datetime
import os

os.environ["ADMIN_API_KEY"] = "secret-admin-key"

from app.db.session import SessionLocal
from app.db.models.monitoring import DriftRun

API_BASE = "http://localhost:8000/api/v1"
ADMIN_HEADERS = {"X-API-Key": "secret-admin-key"}

def test_drift_spike():
    # Insert a critical drift run directly into DB
    db = SessionLocal()
    try:
        drift = DriftRun(
            drift_score=0.35,
            status="CRITICAL",
            recommended_action="Recommend immediate retraining.",
            reference_dataset_id="test_dataset",
            current_window_start=datetime.datetime.now(datetime.timezone.utc),
            current_window_end=datetime.datetime.now(datetime.timezone.utc),
            input_distribution={"feature_1_drift": 0.4}
        )
        db.add(drift)
        db.commit()
    finally:
        db.close()
        
    response = requests.get(f"{API_BASE}/drift/latest", headers=ADMIN_HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "CRITICAL"
    assert "retraining" in data["recommended_action"].lower()

def test_failed_quality_gate():
    pass

def test_deployment_health_failure_and_rollback():
    response = requests.post(f"{API_BASE}/models/nonexistent/rollback", headers=ADMIN_HEADERS)
    assert response.status_code in [404, 400] 
