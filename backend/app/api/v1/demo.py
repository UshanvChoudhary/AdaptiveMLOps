import json
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.dependencies import get_db
from app.db.models.prediction import Prediction
from app.db.models.feedback import Feedback
from app.db.models.registry import ModelVersion, Dataset, TrainingRun, EvaluationRun
from app.db.models.deployment import Deployment, DeploymentStatus
from app.db.models.retraining import RetrainingJob
from app.db.models.governance import AuditLog, AuditAction
from app.db.models.monitoring import DriftRun, DriftStatus

router = APIRouter()

async def get_or_create_demo_training_run(db: AsyncSession) -> TrainingRun:
    ds_res = await db.execute(select(Dataset).where(Dataset.version == "demo-dataset-v1"))
    dataset = ds_res.scalars().first()
    if not dataset:
        dataset = Dataset(version="demo-dataset-v1", checksum="demo-checksum-hash-12345")
        db.add(dataset)
        await db.flush()

    tr_res = await db.execute(select(TrainingRun).where(TrainingRun.dataset_id == dataset.id))
    tr = tr_res.scalars().first()
    if not tr:
        tr = TrainingRun(
            dataset_id=dataset.id,
            git_commit="c0ffee1234567890abcdef1234567890abcdef12",
            hyperparameters={"n_estimators": 100, "max_depth": 5, "learning_rate": 0.1},
            status="SUCCESS"
        )
        db.add(tr)
        await db.flush()
    return tr

@router.post("/seed")
async def seed_demo_data(db: AsyncSession = Depends(get_db)):
    tr = await get_or_create_demo_training_run(db)
    
    # Check if v1.0 exists
    res = await db.execute(select(ModelVersion).where(ModelVersion.version == "v1.0"))
    version = res.scalars().first()
    if not version:
        version = ModelVersion(
            version="v1.0",
            algorithm="xgboost",
            status="DEPLOYED",
            artifact_path="/ml/artifacts/1.0.0",
            training_run_id=tr.id
        )
        db.add(version)
        await db.flush()

        dep = Deployment(
            model_version_id=version.id,
            image_tag="v1.0.0",
            environment="production",
            status=DeploymentStatus.SUCCESS,
            actor="admin"
        )
        db.add(dep)
    
    audit = AuditLog(
        action=AuditAction.DEPLOYMENT_SUCCEEDED,
        actor="professor",
        details=json.dumps({"version": "v1.0", "status": "seeded"})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Demo seeded successfully"}

@router.post("/feedback")
async def generate_demo_feedback(db: AsyncSession = Depends(get_db)):
    pred = Prediction(
        model_version="v1.0",
        input_text="Demo fraud detection sample transaction data",
        predicted_label="legit",
        confidence=0.985,
        latency_ms=14.2,
        trace_id=uuid.uuid4()
    )
    db.add(pred)
    await db.flush()
    
    fb = Feedback(
        prediction_id=pred.id,
        user_id="professor",
        is_correct=True,
        feedback_status="processed"
    )
    db.add(fb)
    
    audit = AuditLog(
        action=AuditAction.FEEDBACK_SUBMITTED,
        actor="professor",
        details=json.dumps({"prediction_id": str(pred.id), "is_correct": True})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Feedback generated", "prediction_id": str(pred.id)}

@router.post("/retrain")
async def trigger_demo_retraining(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    tr = await get_or_create_demo_training_run(db)
    job = RetrainingJob(
        trigger_type="MANUAL",
        reason="Demonstration retraining trigger via UI",
        feedback_count=15,
        dataset_id=tr.dataset_id,
        status="COMPLETED"
    )
    db.add(job)
    await db.flush()
    
    audit = AuditLog(
        action=AuditAction.RETRAINING_TRIGGERED,
        actor="professor",
        details=json.dumps({"job_id": str(job.id), "trigger": "UI"})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Retraining triggered", "job_id": str(job.id)}

@router.post("/challenger/good")
async def create_good_challenger(db: AsyncSession = Depends(get_db)):
    tr = await get_or_create_demo_training_run(db)
    res = await db.execute(select(ModelVersion).where(ModelVersion.version == "v1.1-good"))
    version = res.scalars().first()
    if not version:
        version = ModelVersion(
            version="v1.1-good",
            algorithm="xgboost",
            status="CANDIDATE",
            artifact_path="demo/artifacts/v1.1-good",
            training_run_id=tr.id
        )
        db.add(version)
        await db.flush()

    eval_run = EvaluationRun(
        model_version_id=version.id,
        dataset_id=tr.dataset_id,
        metrics={"accuracy": 0.942, "f1_score": 0.935, "latency_p99_ms": 18.4}
    )
    db.add(eval_run)

    audit = AuditLog(
        action=AuditAction.TRAINING_COMPLETED,
        actor="professor",
        details=json.dumps({"version": "v1.1-good", "metrics": eval_run.metrics})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Good challenger created", "metrics": eval_run.metrics}

@router.post("/challenger/bad")
async def create_bad_challenger(db: AsyncSession = Depends(get_db)):
    tr = await get_or_create_demo_training_run(db)
    res = await db.execute(select(ModelVersion).where(ModelVersion.version == "v1.1-bad"))
    version = res.scalars().first()
    if not version:
        version = ModelVersion(
            version="v1.1-bad",
            algorithm="xgboost",
            status="CANDIDATE",
            artifact_path="demo/artifacts/v1.1-bad",
            training_run_id=tr.id
        )
        db.add(version)
        await db.flush()

    eval_run = EvaluationRun(
        model_version_id=version.id,
        dataset_id=tr.dataset_id,
        metrics={"accuracy": 0.621, "f1_score": 0.584, "latency_p99_ms": 120.0}
    )
    db.add(eval_run)

    audit = AuditLog(
        action=AuditAction.TRAINING_COMPLETED,
        actor="professor",
        details=json.dumps({"version": "v1.1-bad", "metrics": eval_run.metrics})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Bad challenger created", "metrics": eval_run.metrics}

@router.post("/quality-gate")
async def run_quality_gate(db: AsyncSession = Depends(get_db)):
    # Update candidate versions based on metrics
    await db.execute(
        update(ModelVersion).where(ModelVersion.version == "v1.1-good").values(status="APPROVED")
    )
    await db.execute(
        update(ModelVersion).where(ModelVersion.version == "v1.1-bad").values(status="REJECTED")
    )
    
    audit = AuditLog(
        action=AuditAction.MODEL_APPROVED,
        actor="quality_gate",
        details=json.dumps({"status": "v1.1-good PASSED quality gate; v1.1-bad REJECTED"})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Quality gate run complete: v1.1-good APPROVED, v1.1-bad REJECTED"}

@router.post("/promote")
async def promote_model(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ModelVersion).where(ModelVersion.version == "v1.1-good"))
    good_ver = res.scalars().first()
    
    await db.execute(
        update(ModelVersion).where(ModelVersion.version == "v1.0").values(status="ARCHIVED")
    )
    if good_ver:
        good_ver.status = "DEPLOYED"
        dep = Deployment(
            model_version_id=good_ver.id,
            image_tag="v1.1-good",
            environment="production",
            status=DeploymentStatus.SUCCESS,
            actor="professor"
        )
        db.add(dep)
        
    audit = AuditLog(
        action=AuditAction.MODEL_APPROVED,
        actor="professor",
        details=json.dumps({"promoted_version": "v1.1-good", "action": "promote_to_production"})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Model v1.1-good promoted to DEPLOYED"}

@router.post("/deploy/fail")
async def simulate_deployment_failure(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ModelVersion).where(ModelVersion.status.in_(["DEPLOYED", "APPROVED"])))
    ver = res.scalars().first()
    if ver:
        dep = Deployment(
            model_version_id=ver.id,
            image_tag="canary-broken-tag",
            environment="production",
            status=DeploymentStatus.FAILED,
            actor="professor"
        )
        db.add(dep)
        
    audit = AuditLog(
        action=AuditAction.DEPLOYMENT_FAILED,
        actor="system",
        details=json.dumps({"status": "Deployment failed simulated", "reason": "Canary health check timeout"})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Deployment failure simulated"}

@router.post("/rollback")
async def demo_rollback(db: AsyncSession = Depends(get_db)):
    # Rollback to v1.0
    await db.execute(
        update(ModelVersion).where(ModelVersion.version == "v1.0").values(status="DEPLOYED")
    )
    await db.execute(
        update(ModelVersion).where(ModelVersion.version == "v1.1-good").values(status="ARCHIVED")
    )
    
    audit = AuditLog(
        action=AuditAction.ROLLBACK,
        actor="professor",
        details=json.dumps({"status": "Rollback to v1.0 executed"})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Rollback to v1.0 executed successfully"}

@router.post("/drift")
async def simulate_drift(db: AsyncSession = Depends(get_db)):
    alert = DriftRun(
        status=DriftStatus.CRITICAL,
        drift_score=0.88,
        recommended_action="Significant covariate shift detected. Trigger retraining pipeline."
    )
    db.add(alert)
    audit = AuditLog(
        action=AuditAction.RETRAINING_TRIGGERED,
        actor="drift_monitor",
        details=json.dumps({"feature": "transaction_amount", "score": 0.88, "threshold": 0.5})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Critical drift simulated (score=0.88)"}
