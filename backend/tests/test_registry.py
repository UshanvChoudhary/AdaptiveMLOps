import pytest
from app.main import app
from app.db.session import Base
from app.dependencies import get_db
from app.db.models.registry import Dataset, TrainingRun, ModelVersion
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

async def test_list_models(client, async_db):
    dataset = Dataset(version="v1.0", checksum="abc")
    async_db.add(dataset)
    await async_db.commit()

    run = TrainingRun(dataset_id=dataset.id, git_commit="123", hyperparameters={"lr": 0.01}, status="COMPLETED")
    async_db.add(run)
    await async_db.commit()

    model = ModelVersion(version="v1.0.0", algorithm="RandomForest", training_run_id=run.id, artifact_path="some/path", status="CANDIDATE")
    async_db.add(model)
    await async_db.commit()

    response = await client.get("/api/v1/models/")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) >= 1

    found = next(m for m in data["models"] if m["version"] == "v1.0.0")
    assert found["algorithm"] == "RandomForest"
    assert found["status"] == "CANDIDATE"
    assert found["training_run"]["git_commit"] == "123"
    assert found["training_run"]["dataset"] is not None

from app.db.models.registry import EvaluationRun

async def test_manual_approve_reject(client, async_db):
    dataset = Dataset(version="v1.1", checksum="abc1")
    async_db.add(dataset)
    await async_db.commit()

    run = TrainingRun(dataset_id=dataset.id, git_commit="1234", hyperparameters={"lr": 0.01}, status="COMPLETED")
    async_db.add(run)
    await async_db.commit()

    model1 = ModelVersion(version="v1.1.0", algorithm="RF", training_run_id=run.id, artifact_path="path", status="CANDIDATE")
    async_db.add(model1)
    
    model2 = ModelVersion(version="v1.1.1", algorithm="RF", training_run_id=run.id, artifact_path="path2", status="CANDIDATE")
    async_db.add(model2)
    await async_db.commit()

    # Approve
    response = await client.post("/api/v1/models/v1.1.0/approve", headers={"X-API-Key": "secret-admin-key"})
    assert response.status_code == 200
    assert response.json()["status"] == "PRODUCTION"

    # Reject
    response2 = await client.post("/api/v1/models/v1.1.1/reject", headers={"X-API-Key": "secret-admin-key"})
    assert response2.status_code == 200
    assert response2.json()["status"] == "REJECTED"


async def test_promote_deliberately_bad_model(client, async_db):
    dataset = Dataset(version="v1.2", checksum="abc2")
    async_db.add(dataset)
    await async_db.commit()

    run = TrainingRun(dataset_id=dataset.id, git_commit="12345", hyperparameters={"lr": 0.01}, status="COMPLETED")
    async_db.add(run)
    await async_db.commit()

    # This is our deliberately bad model
    model = ModelVersion(version="v1.2.0-bad", algorithm="RF", training_run_id=run.id, artifact_path="path", status="CANDIDATE")
    async_db.add(model)
    await async_db.commit()
    
    # Add bad evaluation metrics
    eval_run = EvaluationRun(
        model_version_id=model.id, 
        dataset_id=dataset.id, 
        metrics={"f1": 0.4, "accuracy": 0.5, "latency_p95_ms": 200.0}
    )
    async_db.add(eval_run)
    await async_db.commit()

    response = await client.post("/api/v1/models/v1.2.0-bad/promote", headers={"X-API-Key": "secret-admin-key"})
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "REJECT"
    assert "below minimum thresholds" in data["reason"].lower() or "latency too high" in data["reason"].lower()

    # Check status updated in db
    await async_db.refresh(model)
    assert model.status == "REJECTED"
