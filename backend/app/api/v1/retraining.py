from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_current_admin_or_api_key
from app.db import session as db_session
from app.schemas.retraining import RetrainingTriggerRequest, RetrainingJobResponse, RetrainingJobListResponse
from app.services.retraining_service import trigger_retraining, run_retraining_job
from app.db.models.retraining import RetrainingJob
import uuid
import asyncio


router = APIRouter(prefix="/retraining", tags=["retraining"])


async def run_job_background(job_id: uuid.UUID):
    async with db_session.SessionLocal() as db:
        await run_retraining_job(db, job_id)

@router.post("/trigger", response_model=RetrainingJobResponse, dependencies=[Depends(get_current_admin_or_api_key)])
async def trigger_job(
    request: RetrainingTriggerRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    try:
        job = await trigger_retraining(db, request)
        # Using a ProcessPoolExecutor to avoid blocking the event loop with CPU bound tasks
        background_tasks.add_task(run_job_background, job.id)
        return job
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/jobs", response_model=RetrainingJobListResponse)
async def list_jobs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    total = (await db.execute(select(func.count(RetrainingJob.id)))).scalar()
    jobs = (await db.execute(select(RetrainingJob).order_by(RetrainingJob.created_at.desc()).offset(skip).limit(limit))).scalars().all()
    return {"jobs": jobs, "total": total}

@router.get("/jobs/{job_id}", response_model=RetrainingJobResponse)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    job = (await db.execute(select(RetrainingJob).filter(RetrainingJob.id == job_id))).scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
