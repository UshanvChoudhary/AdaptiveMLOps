from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
import uuid

from app.dependencies import get_db
from app.db.models.prediction import Prediction
from app.db.models.feedback import Feedback
from app.db.models.registry import ModelVersion
from app.db.models.retraining import RetrainingJob
from app.db.models.governance import AuditLog
from app.db.models.monitoring import DriftRun, DriftStatus
from app.services.retraining_service import run_retraining_job

router = APIRouter()

@router.post("/seed")
async def seed_demo_data(db: AsyncSession = Depends(get_db)):
    version = ModelVersion(version="v1.0", algorithm="xgboost", status="DEPLOYED", artifact_path="demo")
    db.add(version)
    await db.commit()
    
    audit = AuditLog(
        action="DEMO_SEED",
        actor="professor",
        details={"status": "seeded"}
    )
    db.add(audit)
    await db.commit()
    return {"status": "Demo seeded successfully"}

@router.post("/feedback")
async def generate_demo_feedback(db: AsyncSession = Depends(get_db)):
    pred = Prediction(
        features={"features": [1,2,3]},
        prediction=1,
        model_version="v1.0",
        probability=0.99, is_champion=True
    )
    db.add(pred)
    await db.commit()
    await db.refresh(pred)
    
    fb = Feedback(
        prediction_id=pred.id,
        actual_value=1,
        user_id="professor",
        is_correct=True,
        feedback_status="processed"
    )
    db.add(fb)
    
    audit = AuditLog(
        action="DEMO_FEEDBACK",
        actor="professor",
        details={"prediction_id": str(pred.id)}
    )
    db.add(audit)
    await db.commit()
    return {"status": "Feedback generated"}

@router.post("/retrain")
async def trigger_demo_retraining(background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    job = RetrainingJob(
        trigger_type="MANUAL",
        reason="Demo trigger",
        feedback_count=1,
        status="QUEUED"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    
    audit = AuditLog(
        action="DEMO_RETRAIN",
        actor="professor",
        details={"job_id": str(job.id)}
    )
    db.add(audit)
    await db.commit()
    
    return {"status": "Retraining triggered", "job_id": job.id}

@router.post("/challenger/good")
async def create_good_challenger(db: AsyncSession = Depends(get_db)):
    version = ModelVersion(version="v1.1-good", algorithm="xgboost", status="CANDIDATE", artifact_path="demo")
    db.add(version)
    audit = AuditLog(
        action="DEMO_GOOD_CHALLENGER",
        actor="professor",
        details={"version": "v1.1-good"}
    )
    db.add(audit)
    await db.commit()
    return {"status": "Good challenger created"}

@router.post("/challenger/bad")
async def create_bad_challenger(db: AsyncSession = Depends(get_db)):
    version = ModelVersion(version="v1.1-bad", algorithm="xgboost", status="CANDIDATE", artifact_path="demo")
    db.add(version)
    audit = AuditLog(
        action="DEMO_BAD_CHALLENGER",
        actor="professor",
        details={"version": "v1.1-bad"}
    )
    db.add(audit)
    await db.commit()
    return {"status": "Bad challenger created"}

@router.post("/quality-gate")
async def run_quality_gate(db: AsyncSession = Depends(get_db)):
    audit = AuditLog(
        action="DEMO_QUALITY_GATE",
        actor="professor",
        details={"status": "Quality gate executed"}
    )
    db.add(audit)
    await db.commit()
    return {"status": "Quality gate run complete"}

@router.post("/promote")
async def promote_model(db: AsyncSession = Depends(get_db)):
    audit = AuditLog(
        action="DEMO_PROMOTE",
        actor="professor",
        details={"status": "Model promoted"}
    )
    db.add(audit)
    await db.commit()
    return {"status": "Model promoted"}

@router.post("/deploy/fail")
async def simulate_deployment_failure(db: AsyncSession = Depends(get_db)):
    audit = AuditLog(
        action="DEMO_DEPLOY_FAIL",
        actor="professor",
        details={"status": "Deployment failed simulated"}
    )
    db.add(audit)
    await db.commit()
    return {"status": "Deployment failure simulated"}

@router.post("/rollback")
async def demo_rollback(db: AsyncSession = Depends(get_db)):
    audit = AuditLog(
        action="DEMO_ROLLBACK",
        actor="professor",
        details={"status": "Rollback performed"}
    )
    db.add(audit)
    await db.commit()
    return {"status": "Rollback executed"}

@router.post("/drift")
async def simulate_drift(db: AsyncSession = Depends(get_db)):
    alert = DriftRun(
        status=DriftStatus.CRITICAL,
        drift_score=0.85,
        recommended_action="Retrain model"
    )
    db.add(alert)
    audit = AuditLog(
        action="DEMO_DRIFT",
        actor="professor",
        details={"feature": "demo_feature", "score": 0.85}
    )
    db.add(audit)
    await db.commit()
    return {"status": "Drift simulated"}
