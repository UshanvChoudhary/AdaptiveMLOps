import pytest
import uuid
import os
import sqlalchemy
from datetime import timedelta
from unittest.mock import AsyncMock

from app.config import settings
from app.api.v1.auth import create_access_token
from app.db.models.registry import ModelVersion, Dataset, TrainingRun, EvaluationRun
from app.db.models.deployment import Deployment, DeploymentStatus
from app.schemas.governance import RollbackRequest
from app.ml.prediction_service import prediction_service

def make_token(username: str, role: str):
    return create_access_token(data={"sub": username, "role": role}, expires_delta=timedelta(minutes=15))

# Scenario 1: Invalid login
async def test_scenario_invalid_login(monkeypatch, client):
    monkeypatch.setattr(settings, "ENABLE_DEMO_MODE", True)
    # Incorrect password
    res = await client.post("/api/v1/auth/token", data={"username": "admin", "password": "wrongpassword"})
    assert res.status_code == 400
    assert "Incorrect username or password" in res.json()["detail"]

    # Non-existent user
    res2 = await client.post("/api/v1/auth/token", data={"username": "fake_user", "password": "password"})
    assert res2.status_code == 400

# Scenario 2: Unauthenticated promotion attempt
async def test_scenario_unauthenticated_promotion(client):
    res = await client.post("/api/v1/models/v1.0.0/promote")
    assert res.status_code == 401
    assert "detail" in res.json()

# Scenario 3: USER attempting ADMIN actions
async def test_scenario_user_attempting_admin_actions(client):
    user_token = make_token("standard_user", "USER")
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # User cannot promote
    res = await client.post("/api/v1/models/v1.0.0/promote", headers=headers)
    assert res.status_code == 403
    assert "Requires ADMIN role" in res.json()["detail"]

    # User cannot view audit logs
    res2 = await client.get("/api/v1/governance/audit-logs", headers=headers)
    assert res2.status_code == 403
    assert "Requires ADMIN role" in res2.json()["detail"]

# Scenario 4: Bad challenger rejected by quality gates
async def test_scenario_bad_challenger_rejected(client, async_db):
    uid = uuid.uuid4().hex[:6]
    ds = Dataset(version=f"ds-bad-{uid}", checksum="checksum123")
    async_db.add(ds)
    await async_db.commit()

    tr = TrainingRun(dataset_id=ds.id, git_commit="git123", hyperparameters={}, status="COMPLETED")
    async_db.add(tr)
    await async_db.commit()

    # Create champion model in PRODUCTION
    champ = ModelVersion(
        version=f"champ-{uid}",
        algorithm="Logistic Regression + TF-IDF",
        training_run_id=tr.id,
        artifact_path="ml/artifacts/1.0.0",
        status="PRODUCTION"
    )
    async_db.add(champ)
    await async_db.commit()

    champ_eval = EvaluationRun(
        model_version_id=champ.id,
        dataset_id=ds.id,
        metrics={"f1": 0.88, "accuracy": 0.90, "latency_p95_ms": 25.0}
    )
    async_db.add(champ_eval)

    # Create bad candidate
    bad_cand = ModelVersion(
        version=f"cand-bad-{uid}",
        algorithm="Logistic Regression + TF-IDF",
        training_run_id=tr.id,
        artifact_path="ml/artifacts/1.0.0",
        status="CANDIDATE"
    )
    async_db.add(bad_cand)
    await async_db.commit()

    bad_eval = EvaluationRun(
        model_version_id=bad_cand.id,
        dataset_id=ds.id,
        metrics={"f1": 0.45, "accuracy": 0.52, "latency_p95_ms": 150.0}
    )
    async_db.add(bad_eval)
    await async_db.commit()

    # Attempt promotion with Admin credentials
    res = await client.post(
        f"/api/v1/models/{bad_cand.version}/promote",
        headers={"X-API-Key": "secret-admin-key"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "REJECT"

    # Verify candidate is REJECTED and champion remains PRODUCTION
    await async_db.refresh(bad_cand)
    await async_db.refresh(champ)
    assert bad_cand.status == "REJECTED"
    assert champ.status == "PRODUCTION"

# Scenario 5: Missing or invalid model artifact rejected
async def test_scenario_missing_model_artifact_rejected(client, async_db):
    uid = uuid.uuid4().hex[:6]
    ds = Dataset(version=f"ds-ghost-{uid}", checksum="ghost123")
    async_db.add(ds)
    await async_db.commit()

    tr = TrainingRun(dataset_id=ds.id, git_commit="ghost", hyperparameters={}, status="COMPLETED")
    async_db.add(tr)
    await async_db.commit()

    # Candidate with non-existent artifact path
    ghost_cand = ModelVersion(
        version=f"cand-ghost-{uid}",
        algorithm="Logistic Regression + TF-IDF",
        training_run_id=tr.id,
        artifact_path="ml/artifacts/non_existent_directory_xyz",
        status="CANDIDATE"
    )
    async_db.add(ghost_cand)
    await async_db.commit()

    # Add passing metrics
    ghost_eval = EvaluationRun(
        model_version_id=ghost_cand.id,
        dataset_id=ds.id,
        metrics={"f1": 0.95, "accuracy": 0.96, "latency_p95_ms": 15.0}
    )
    async_db.add(ghost_eval)
    await async_db.commit()

    res = await client.post(
        f"/api/v1/models/{ghost_cand.version}/promote",
        headers={"X-API-Key": "secret-admin-key"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "REJECT"
    assert "does not exist on disk" in data["reason"]
    await async_db.refresh(ghost_cand)
    assert ghost_cand.status == "REJECTED"

# Scenario 6: Database unavailable returns 503 on /ready
async def test_scenario_database_unavailable_returns_503(monkeypatch, client):
    from app.dependencies import get_db
    from app.main import app
    
    async def failing_db():
        mock_session = AsyncMock()
        mock_session.execute.side_effect = Exception("Connection to PostgreSQL failed: connection refused")
        yield mock_session

    app.dependency_overrides[get_db] = failing_db
    try:
        res = await client.get("/api/v1/ready")
        assert res.status_code == 503
        assert "Database connectivity check failed" in res.json()["detail"]
    finally:
        app.dependency_overrides.pop(get_db, None)

# Scenario 7: Training job failure recording
async def test_scenario_training_job_failure_recorded(client, async_db):
    await async_db.execute(sqlalchemy.text('DELETE FROM feedback'))
    await async_db.execute(sqlalchemy.text('DELETE FROM retraining_jobs'))
    await async_db.commit()

    res = await client.post("/api/v1/retraining/trigger", headers={"X-API-Key": "secret-admin-key"}, json={
        "trigger_type": "MANUAL",
        "reason": "Negative test no feedback"
    })
    assert res.status_code == 200
    job_id = res.json()["id"]

    import time
    time.sleep(1)

    res2 = await client.get(f"/api/v1/retraining/jobs/{job_id}")
    assert res2.status_code == 200
    job_data = res2.json()
    assert job_data["status"] == "FAILED"
    assert "No eligible feedback" in job_data["error_message"]

# Scenario 8: Deployment health-check failure
async def test_scenario_deployment_health_check_failure(client, async_db):
    uid = uuid.uuid4().hex[:6]
    ds = Dataset(version=f"ds-dep-{uid}", checksum="dep123")
    async_db.add(ds)
    await async_db.commit()

    tr = TrainingRun(dataset_id=ds.id, git_commit="dep", hyperparameters={}, status="COMPLETED")
    async_db.add(tr)
    await async_db.commit()

    model = ModelVersion(
        version=f"dep-model-{uid}",
        algorithm="Logistic Regression + TF-IDF",
        training_run_id=tr.id,
        artifact_path="ml/artifacts/1.0.0",
        status="PRODUCTION"
    )
    async_db.add(model)
    await async_db.commit()

    # Create deployment
    dep_res = await client.post("/api/v1/deployments", headers={"X-API-Key": "secret-admin-key"}, json={
        "model_version_id": str(model.id),
        "image_tag": f"img-{uid}",
        "environment": "STAGING",
        "actor": "jenkins"
    })
    assert dep_res.status_code == 200
    dep_id = dep_res.json()["id"]

    # Post unhealthy check
    hc_res = await client.post(f"/api/v1/deployments/{dep_id}/health", headers={"X-API-Key": "secret-admin-key"}, json={
        "endpoint": "/ready",
        "status_code": "503",
        "response_time_ms": "5000",
        "is_healthy": False,
        "details": "Model service crashed"
    })
    assert hc_res.status_code == 200

    # Mark deployment FAILED
    patch_res = await client.patch(f"/api/v1/deployments/{dep_id}", headers={"X-API-Key": "secret-admin-key"}, json={
        "status": "FAILED",
        "health_result": {"healthy": False, "failed_check": "/ready"}
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "FAILED"

# Scenario 9: Rollback restores previous validated artifact and deployment
async def test_scenario_rollback_restores_artifact(client, async_db):
    uid = uuid.uuid4().hex[:6]
    ds = Dataset(version=f"ds-roll-{uid}", checksum="roll123")
    async_db.add(ds)
    await async_db.commit()

    tr = TrainingRun(dataset_id=ds.id, git_commit="roll", hyperparameters={}, status="COMPLETED")
    async_db.add(tr)
    await async_db.commit()

    # Previous healthy model (v1.0)
    prev_model = ModelVersion(
        version=f"v1.0-prev-{uid}",
        algorithm="Logistic Regression + TF-IDF",
        training_run_id=tr.id,
        artifact_path="ml/artifacts/1.0.0",
        status="ARCHIVED"
    )
    async_db.add(prev_model)
    await async_db.commit()

    prev_dep = Deployment(
        id=uuid.uuid4(),
        model_version_id=prev_model.id,
        image_tag=f"img-prev-{uid}",
        environment="production",
        status=DeploymentStatus.SUCCESS,
        actor="admin"
    )
    async_db.add(prev_dep)
    await async_db.commit()

    # Current model that needs rollback
    curr_model = ModelVersion(
        version=f"v2.0-curr-{uid}",
        algorithm="Logistic Regression + TF-IDF",
        training_run_id=tr.id,
        artifact_path="ml/artifacts/1.0.0",
        status="PRODUCTION"
    )
    async_db.add(curr_model)
    await async_db.commit()

    admin_token = make_token("admin_user", "ADMIN")
    headers = {"Authorization": f"Bearer {admin_token}"}

    res = await client.post(
        f"/api/v1/governance/models/{curr_model.version}/rollback",
        headers=headers,
        json={"target_version": prev_model.version, "reason": "Severe regression detected in production"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["rolled_back_to"] == prev_model.version

    # Check statuses in database
    await async_db.refresh(curr_model)
    await async_db.refresh(prev_model)
    assert curr_model.status == "ARCHIVED"
    assert prev_model.status == "PRODUCTION"

    # Check that in-memory prediction service loaded the artifact
    assert prediction_service.model is not None

# Scenario 10: Drift alert without automatic deployment
async def test_scenario_drift_alert_without_auto_deployment(monkeypatch, client, async_db):
    monkeypatch.setattr(settings, "ENABLE_DEMO_MODE", True)

    # Record current deployment count
    from app.db.models.deployment import Deployment
    initial_dep_count = (await async_db.execute(sqlalchemy.select(sqlalchemy.func.count(Deployment.id)))) .scalar()

    # Trigger critical drift alert
    res = await client.post("/api/v1/demo/drift")
    assert res.status_code == 200
    assert "Critical drift simulated" in res.json()["status"]

    # Verify no automatic deployment was created
    new_dep_count = (await async_db.execute(sqlalchemy.select(sqlalchemy.func.count(Deployment.id)))) .scalar()
    assert new_dep_count == initial_dep_count
