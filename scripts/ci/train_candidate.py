import sys
import os
os.environ["ADMIN_API_KEY"] = "secret-admin-key"
os.environ["BACKEND_CORS_ORIGINS"] = '["http://localhost:5173"]'
import json
import time
import asyncio
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.db.models.feedback import Feedback
from app.db.models.prediction import Prediction

async def seed_feedback():
    async with SessionLocal() as db:
        pred = Prediction(
            id=uuid.uuid4(),
            model_version="v1.0.0",
            input_text="Test",
            predicted_label="A",
            confidence=0.9,
            latency_ms=10.0,
            trace_id=uuid.uuid4()
        )
        db.add(pred)
        await db.commit()
        
        fb = Feedback(
            prediction_id=pred.id,
            is_correct=False,
            corrected_label="B",
            feedback_status="pending"
        )
        db.add(fb)
        await db.commit()

asyncio.run(seed_feedback())

with TestClient(app) as client:
    print("Triggering candidate training...")
    res = client.post("/api/v1/retraining/trigger", json={"trigger_type": "MANUAL"}, headers={"X-API-Key": "secret-admin-key"})
    if res.status_code == 200:
        print(f"Candidate trained. Job details: {res.json()}")
        time.sleep(3)  # Give background task time to execute
        
        # Verify candidate actually exists
        models_res = client.get("/api/v1/models/")
        candidates = [m for m in models_res.json().get("models", []) if m["status"] == "CANDIDATE"]
        cand_models = [m for m in candidates if m.get("evaluations") or m["version"].startswith("cand-")]
        candidate = cand_models[-1] if cand_models else (candidates[-1] if candidates else None)
        if candidate:
            print(f"Found Candidate: {candidate['version']}")
            sys.exit(0)
        else:
            print("Job succeeded but no CANDIDATE model was found in registry!")
            job_id = res.json()["id"]
            job_res = client.get(f"/api/v1/retraining/jobs/{job_id}")
            print("Job details:", job_res.json())
            sys.exit(1)
    else:
        print(f"Failed to train candidate. Status: {res.status_code}, {res.text}")
        sys.exit(1)
