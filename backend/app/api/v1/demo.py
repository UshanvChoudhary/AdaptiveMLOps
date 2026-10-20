from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import uuid
import json

from app.config import settings
from app.dependencies import get_db
from app.db.models.prediction import Prediction
from app.db.models.feedback import Feedback
from app.db.models.governance import AuditLog, AuditAction
from app.db.models.retraining import RetrainingJob
from app.db.models.registry import ModelVersion, EvaluationRun, TrainingRun, Dataset
from app.db.models.deployment import Deployment, DeploymentStatus
from app.db.models.monitoring import DriftRun, DriftStatus

def verify_demo_mode():
    if not settings.ENABLE_DEMO_MODE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo endpoints are disabled in non-demo environment. Enable ENABLE_DEMO_MODE=true."
        )

router = APIRouter(dependencies=[Depends(verify_demo_mode)])

async def get_or_create_demo_training_run(db: AsyncSession):
    ds_res = await db.execute(select(Dataset).where(Dataset.version == "demo"))
    ds = ds_res.scalars().first()
    if not ds:
        ds = Dataset(
            version="demo",
            checksum="73e460ee5c8b1c5d748aed2e2722b8a2bca9adfc032941490f5deedc4af4e9fb"
        )
        db.add(ds)
        await db.flush()

    tr_res = await db.execute(select(TrainingRun).where(TrainingRun.dataset_id == ds.id))
    tr = tr_res.scalars().first()
    if not tr:
        tr = TrainingRun(
            dataset_id=ds.id,
            git_commit="git-init-sha",
            hyperparameters={"C": 1.0, "penalty": "l2", "solver": "lbfgs"},
            status="COMPLETED"
        )
        db.add(tr)
        await db.flush()
    return tr

@router.post("/seed")
async def seed_demo_environment(db: AsyncSession = Depends(get_db)):
    tr = await get_or_create_demo_training_run(db)
    res = await db.execute(select(ModelVersion).where(ModelVersion.version == "v1.0"))
    version = res.scalars().first()
    if not version:
        version = ModelVersion(
            version="v1.0",
            algorithm="Logistic Regression + TF-IDF",
            status="PRODUCTION",
            artifact_path="ml/artifacts/1.0.0",
            training_run_id=tr.id
        )
        db.add(version)
        await db.flush()
        
        eval_run = EvaluationRun(
            model_version_id=version.id,
            dataset_id=tr.dataset_id,
            metrics={"accuracy": 0.895, "f1_score": 0.887, "f1": 0.887, "latency_p95_ms": 14.2}
        )
        db.add(eval_run)
        
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
        actor="demo_system",
        details=json.dumps({"version": "v1.0", "status": "seeded", "type": "seeded_demo_metrics"})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Demo seeded successfully"}

@router.post("/feedback")
async def generate_demo_feedback(db: AsyncSession = Depends(get_db)):
    pred = Prediction(
        model_version="v1.0",
        input_text="I was charged twice on my monthly invoice for renewal",
        predicted_label="technical_support",
        confidence=0.82,
        latency_ms=14.2,
        trace_id=uuid.uuid4()
    )
    db.add(pred)
    await db.flush()
    
    fb = Feedback(
        prediction_id=pred.id,
        user_id="customer",
        is_correct=False,
        corrected_label="billing",
        comments="Should be billing intent, not technical support",
        feedback_status="pending"
    )
    db.add(fb)
    
    audit = AuditLog(
        action=AuditAction.FEEDBACK_SUBMITTED,
        actor="customer",
        details=json.dumps({"prediction_id": str(pred.id), "is_correct": False, "corrected_label": "billing"})
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
        feedback_count=1,
        dataset_id=tr.dataset_id,
        status="COMPLETED"
    )
    db.add(job)
    await db.flush()
    
    audit = AuditLog(
        action=AuditAction.RETRAINING_TRIGGERED,
        actor="admin",
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
            algorithm="Logistic Regression + TF-IDF",
            status="CANDIDATE",
            artifact_path="ml/artifacts/1.0.0",
            training_run_id=tr.id
        )
        db.add(version)
        await db.flush()

    eval_run = EvaluationRun(
        model_version_id=version.id,
        dataset_id=tr.dataset_id,
        metrics={"accuracy": 0.942, "f1_score": 0.935, "f1": 0.935, "latency_p95_ms": 18.4, "metric_type": "seeded_demo"}
    )
    db.add(eval_run)

    audit = AuditLog(
        action=AuditAction.TRAINING_COMPLETED,
        actor="demo_system",
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
            algorithm="Logistic Regression + TF-IDF",
            status="CANDIDATE",
            artifact_path="ml/artifacts/1.0.0",
            training_run_id=tr.id
        )
        db.add(version)
        await db.flush()

    eval_run = EvaluationRun(
        model_version_id=version.id,
        dataset_id=tr.dataset_id,
        metrics={"accuracy": 0.621, "f1_score": 0.584, "f1": 0.584, "latency_p95_ms": 120.0, "metric_type": "seeded_demo"}
    )
    db.add(eval_run)

    audit = AuditLog(
        action=AuditAction.TRAINING_COMPLETED,
        actor="demo_system",
        details=json.dumps({"version": "v1.1-bad", "metrics": eval_run.metrics})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Bad challenger created", "metrics": eval_run.metrics}

@router.post("/quality-gate")
async def run_quality_gate(db: AsyncSession = Depends(get_db)):
    await db.execute(
        update(ModelVersion).where(ModelVersion.version == "v1.1-good").values(status="APPROVED")
    )
    await db.execute(
        update(ModelVersion).where(ModelVersion.version == "v1.1-bad").values(status="REJECTED")
    )
    
    audit = AuditLog(
        action=AuditAction.MODEL_APPROVED,
        actor="quality_gate",
        details=json.dumps({"status": "v1.1-good PASSED quality gate (F1: 0.935); v1.1-bad REJECTED (F1: 0.584)"})
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
        good_ver.status = "PRODUCTION"
        dep = Deployment(
            model_version_id=good_ver.id,
            image_tag="v1.1-good",
            environment="production",
            status=DeploymentStatus.SUCCESS,
            actor="admin"
        )
        db.add(dep)
        
    audit = AuditLog(
        action=AuditAction.MODEL_APPROVED,
        actor="admin",
        details=json.dumps({"promoted_version": "v1.1-good", "action": "promote_to_production"})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Model v1.1-good promoted to PRODUCTION"}

@router.post("/deploy/fail")
async def simulate_deployment_failure(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ModelVersion).where(ModelVersion.status.in_(["PRODUCTION", "APPROVED", "DEPLOYED"])))
    ver = res.scalars().first()
    if ver:
        dep = Deployment(
            model_version_id=ver.id,
            image_tag="canary-broken-tag",
            environment="production",
            status=DeploymentStatus.FAILED,
            actor="admin",
            health_result={"error": "Canary health check timeout on /ready"}
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
    await db.execute(
        update(ModelVersion).where(ModelVersion.version == "v1.0").values(status="PRODUCTION")
    )
    await db.execute(
        update(ModelVersion).where(ModelVersion.version == "v1.1-good").values(status="ARCHIVED")
    )
    
    audit = AuditLog(
        action=AuditAction.ROLLBACK,
        actor="admin",
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
        recommended_action="Significant intent distribution shift detected. Retraining recommended."
    )
    db.add(alert)
    audit = AuditLog(
        action=AuditAction.RETRAINING_TRIGGERED,
        actor="drift_monitor",
        details=json.dumps({"feature": "intent_distribution", "score": 0.88, "threshold": 0.30})
    )
    db.add(audit)
    await db.commit()
    return {"status": "Critical drift simulated (score=0.88)"}
