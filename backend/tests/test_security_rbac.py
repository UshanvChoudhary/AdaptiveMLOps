import pytest
import uuid
from datetime import timedelta
from app.config import settings
from app.api.v1.auth import create_access_token
from app.db.models.registry import ModelVersion, Dataset, TrainingRun

def make_token(username: str, role: str):
    return create_access_token(data={"sub": username, "role": role}, expires_delta=timedelta(minutes=15))

@pytest.fixture
async def sample_candidate(async_db):
    uid = uuid.uuid4().hex[:6]
    ds = Dataset(version=f"ds-rbac-{uid}", checksum="dummy")
    async_db.add(ds)
    await async_db.commit()

    tr = TrainingRun(dataset_id=ds.id, git_commit="abc", hyperparameters={}, status="COMPLETED")
    async_db.add(tr)
    await async_db.commit()

    cand = ModelVersion(
        version=f"cand-rbac-{uid}",
        algorithm="Logistic Regression + TF-IDF",
        training_run_id=tr.id,
        artifact_path="ml/artifacts/1.0.0",
        status="CANDIDATE"
    )
    async_db.add(cand)
    await async_db.commit()
    await async_db.refresh(cand)
    cand.test_dataset_id = ds.id
    return cand

async def test_unauthenticated_promotion(client, sample_candidate):
    # No Authorization header or API key
    res = await client.post(f"/api/v1/models/{sample_candidate.version}/promote")
    assert res.status_code == 401
    assert "detail" in res.json()

async def test_unauthenticated_approval(client, sample_candidate):
    # No Authorization header or API key
    res = await client.post(f"/api/v1/models/{sample_candidate.version}/approve")
    assert res.status_code == 401

async def test_unauthenticated_rejection(client, sample_candidate):
    res = await client.post(f"/api/v1/models/{sample_candidate.version}/reject")
    assert res.status_code == 401

async def test_unauthenticated_audit_logs(client):
    res = await client.get("/api/v1/governance/audit-logs")
    assert res.status_code == 401

async def test_user_cannot_promote(client, sample_candidate):
    token = make_token("regular_user", "USER")
    headers = {"Authorization": f"Bearer {token}"}
    res = await client.post(f"/api/v1/models/{sample_candidate.version}/promote", headers=headers)
    assert res.status_code == 403
    assert "Requires ADMIN role" in res.json()["detail"]

async def test_user_cannot_approve(client, sample_candidate):
    token = make_token("regular_user", "USER")
    headers = {"Authorization": f"Bearer {token}"}
    res = await client.post(f"/api/v1/models/{sample_candidate.version}/approve", headers=headers)
    assert res.status_code == 403
    assert "Requires REVIEWER or ADMIN role" in res.json()["detail"]

async def test_user_cannot_view_audit_logs(client):
    token = make_token("regular_user", "USER")
    headers = {"Authorization": f"Bearer {token}"}
    res = await client.get("/api/v1/governance/audit-logs", headers=headers)
    assert res.status_code == 403
    assert "Requires ADMIN role" in res.json()["detail"]

async def test_reviewer_cannot_promote(client, sample_candidate):
    token = make_token("model_reviewer", "REVIEWER")
    headers = {"Authorization": f"Bearer {token}"}
    res = await client.post(f"/api/v1/models/{sample_candidate.version}/promote", headers=headers)
    assert res.status_code == 403
    assert "Requires ADMIN role" in res.json()["detail"]

async def test_reviewer_can_approve(client, sample_candidate):
    token = make_token("model_reviewer", "REVIEWER")
    headers = {"Authorization": f"Bearer {token}"}
    res = await client.post(f"/api/v1/models/{sample_candidate.version}/approve", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "PRODUCTION"

async def test_demo_mode_disabled_blocks_demo_login(monkeypatch, client):
    monkeypatch.setattr(settings, "ENABLE_DEMO_MODE", False)
    res = await client.post("/api/v1/auth/token", data={"username": "admin", "password": "password"})
    assert res.status_code == 401
    assert "Demo credentials disabled" in res.json()["detail"]

async def test_demo_mode_disabled_blocks_demo_endpoints(monkeypatch, client):
    monkeypatch.setattr(settings, "ENABLE_DEMO_MODE", False)
    res = await client.post("/api/v1/demo/retrain")
    assert res.status_code == 403
    assert "Demo endpoints are disabled" in res.json()["detail"]

async def test_admin_token_allows_promote(client, sample_candidate, async_db):
    token = make_token("admin_user", "ADMIN")
    headers = {"Authorization": f"Bearer {token}"}
    from app.db.models.registry import EvaluationRun
    eval_run = EvaluationRun(
        model_version_id=sample_candidate.id,
        dataset_id=sample_candidate.test_dataset_id,
        metrics={"f1": 0.95, "accuracy": 0.95, "latency_p95_ms": 20.0}
    )
    async_db.add(eval_run)
    await async_db.commit()

    res = await client.post(f"/api/v1/models/{sample_candidate.version}/promote", headers=headers)
    assert res.status_code == 200
    assert res.json()["decision"] == "PROMOTE"
