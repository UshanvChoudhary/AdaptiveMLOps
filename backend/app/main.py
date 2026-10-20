import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.router import router
from app.config import settings
from app.ml.prediction_service import prediction_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        prediction_service.load_model()
    except Exception as e:
        print(f"Lifespan model load error: {e}")

    # Resume queued or stuck background jobs
    from app.db.session import SessionLocal
    from app.api.v1.retraining import run_job_background
    from app.db.models.retraining import RetrainingJob
    from sqlalchemy import select
    import asyncio
    
    try:
        async with SessionLocal() as db:
            jobs = (await db.execute(select(RetrainingJob).filter(RetrainingJob.status.in_(["QUEUED", "RUNNING"])))).scalars().all()
            for job in jobs:
                job.status = "QUEUED"
            await db.commit()
            for job in jobs:
                asyncio.create_task(run_job_background(job.id))
    except Exception as e:
        print(f"Lifespan startup error (db might not be ready yet during tests): {e}")
        
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(router, prefix=settings.API_V1_STR)
