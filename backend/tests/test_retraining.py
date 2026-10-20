import pytest
import sqlalchemy
from app.main import app as fastapi_app
from app.db.session import Base
from app.dependencies import get_db
import app.db.session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid
import time
from app.db.models.feedback import Feedback
from app.db.models.registry import ModelVersion, Dataset, TrainingRun

async def test_trigger_manual_retraining(client):
    response = await client.post("/api/v1/retraining/trigger", headers={"X-API-Key": "secret-admin-key"}, json={
        "trigger_type": "MANUAL",
        "reason": "Testing manual trigger"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["trigger_type"] == "MANUAL"
    assert data["status"] == "QUEUED"
    
    # Check if job was created
    response2 = await client.get("/api/v1/retraining/jobs")
    assert response2.status_code == 200
    jobs = response2.json()["jobs"]
    assert len(jobs) > 0
    
    # Wait a bit for background task to run
    time.sleep(1)
    
    # Get specific job
    job_id = data["id"]
    response3 = await client.get(f"/api/v1/retraining/jobs/{job_id}")
    assert response3.status_code == 200
    job_data = response3.json()
    assert job_data["status"] in ["RUNNING", "COMPLETED", "FAILED"]

async def test_trigger_threshold_retraining(client, async_db):
    # Wait for previous jobs to complete to avoid overlap
    import time
    time.sleep(2)
    await async_db.execute(sqlalchemy.text('DELETE FROM retraining_jobs'))
    await async_db.commit()

    response = await client.post("/api/v1/retraining/trigger", headers={"X-API-Key": "secret-admin-key"}, json={
        "trigger_type": "FEEDBACK_THRESHOLD",
        "reason": "Should fail because not enough feedback"
    })
    
    assert response.status_code == 400
    assert "below threshold" in response.json()["detail"]

async def test_retraining_no_eligible_feedback(client, async_db):
    await async_db.execute(sqlalchemy.text('DELETE FROM feedback'))
    await async_db.execute(sqlalchemy.text('DELETE FROM retraining_jobs'))
    await async_db.commit()
    # Trigger a manual job when there is no feedback
    response = await client.post("/api/v1/retraining/trigger", headers={"X-API-Key": "secret-admin-key"}, json={
        "trigger_type": "MANUAL",
        "reason": "Test empty feedback"
    })
    assert response.status_code == 200
    job_id = response.json()["id"]

    # Wait for the background task to finish (since it uses sqlite, it might be fast, but we'll fetch explicitly)
    import time
    time.sleep(1) # wait for bg task

    response = await client.get(f"/api/v1/retraining/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "FAILED"
    assert "No eligible feedback" in data["error_message"]

async def test_retraining_pagination(client, async_db):
    # Add some dummy jobs
    from app.db.models.retraining import RetrainingJob
    for i in range(5):
        async_db.add(RetrainingJob(
            trigger_type="MANUAL",
            feedback_count=0,
            status="COMPLETED"
        ))
    await async_db.commit()

    response = await client.get("/api/v1/retraining/jobs?skip=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["jobs"]) == 2

