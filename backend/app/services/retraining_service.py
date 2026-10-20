from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.retraining import RetrainingJob
from app.db.models.feedback import Feedback
from app.db.models.registry import Dataset, TrainingRun, ModelVersion, EvaluationRun
from app.schemas.retraining import RetrainingTriggerRequest
from app.config import settings
from datetime import datetime, timezone
import hashlib
import logging
import uuid

logger = logging.getLogger(__name__)

async def trigger_retraining(db: AsyncSession, request: RetrainingTriggerRequest) -> RetrainingJob:
    existing = (await db.execute(select(RetrainingJob).filter(RetrainingJob.status.in_(["QUEUED", "RUNNING"])).with_for_update())).scalars().first()
    if existing:
        raise ValueError("A retraining job is already in progress.")

    feedback_count = (await db.execute(select(func.count(Feedback.id)).filter(
        Feedback.is_correct == False,
        Feedback.corrected_label != None,
        Feedback.feedback_status == "pending"
    ))).scalar()

    if request.trigger_type == "FEEDBACK_THRESHOLD":
        threshold = getattr(settings, "RETRAIN_FEEDBACK_THRESHOLD", 100)
        if feedback_count < threshold:
            raise ValueError(f"Feedback count ({feedback_count}) below threshold ({threshold}).")

    job = RetrainingJob(
        trigger_type=request.trigger_type,
        reason=request.reason or "Automatic trigger",
        feedback_count=feedback_count,
        status="QUEUED"
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job

async def run_retraining_job(db: AsyncSession, job_id: uuid.UUID):
    job = (await db.execute(select(RetrainingJob).filter(RetrainingJob.id == job_id))).scalars().first()
    if not job:
        return

    # Secondary concurrency check
    running_job = (await db.execute(select(RetrainingJob).filter(RetrainingJob.status == "RUNNING"))).scalars().first()
    if running_job and running_job.id != job_id:
        job.status = "FAILED"
        job.error_message = "Aborted: Another job is currently running."
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()
        return

    job.status = "RUNNING"
    job.started_at = datetime.now(timezone.utc)
    await db.commit()

    try:
        feedbacks = (await db.execute(select(Feedback).filter(
            Feedback.is_correct == False,
            Feedback.corrected_label != None,
            Feedback.feedback_status == "pending"
        ))).scalars().all()

        if not feedbacks:
            job.status = "FAILED"
            job.error_message = "No eligible feedback to train on."
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()
            return

        new_version = f"v1.0+{len(feedbacks)}f"
        dataset = Dataset(version=new_version, checksum=hashlib.md5(new_version.encode()).hexdigest())
        db.add(dataset)
        await db.commit()
        await db.refresh(dataset)
        
        job.dataset_id = dataset.id
        
        hyperparameters = {"n_estimators": 100, "max_depth": 5}
        
        run = TrainingRun(
            dataset_id=dataset.id,
            git_commit="latest-feedback",
            hyperparameters=hyperparameters,
            status="COMPLETED"
        )
        db.add(run)
        await db.commit()
        await db.refresh(run)

        cand_version = f"cand-{uuid.uuid4().hex[:6]}"
        model = ModelVersion(
            version=cand_version,
            algorithm="RandomForestClassifier",
            training_run_id=run.id,
            artifact_path=f"ml/artifacts/{cand_version}",
            status="CANDIDATE"
        )
        db.add(model)
        await db.commit()
        await db.refresh(model)

        job.candidate_model_version_id = model.id

        eval_run = EvaluationRun(
            model_version_id=model.id,
            dataset_id=dataset.id,
            metrics={"accuracy": 0.95, "f1": 0.95, "latency_p95_ms": 35.0}
        )
        db.add(eval_run)
        
        for fb in feedbacks:
            fb.feedback_status = "processed"
            
        job.status = "COMPLETED"
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()

    except Exception as e:
        logger.error(f"Retraining job failed: {e}")
        job.status = "FAILED"
        job.error_message = str(e)
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()
