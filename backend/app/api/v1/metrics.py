from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.dependencies import get_db
from app.schemas.monitoring import MetricsResponse
from app.db.models.prediction import Prediction
from app.db.models.feedback import Feedback
from app.db.models.registry import EvaluationRun
from app.services.drift_service import get_latest_drift

router = APIRouter()

@router.get("/", response_model=MetricsResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    # 1. Prediction count
    pred_res = await db.execute(select(func.count()).select_from(Prediction))
    prediction_count = pred_res.scalar_one()
    
    # 2. p95 latency & 3. Error rate
    lat_res = await db.execute(
        select(Prediction.latency_ms)
        .where(Prediction.latency_ms.isnot(None))
        .order_by(Prediction.created_at.desc())
        .limit(1000)
    )
    latencies = [r[0] for r in lat_res.all()]
    
    p95_latency = 0.0
    error_rate = 0.0
    
    if latencies:
        latencies.sort()
        idx = int(len(latencies) * 0.95)
        p95_latency = float(latencies[idx])
        error_count = sum(1 for l in latencies if l > 500)
        error_rate = float(error_count / len(latencies))
    
    # 4. Feedback correction rate
    fb_total_res = await db.execute(select(func.count()).select_from(Feedback))
    total_feedbacks = fb_total_res.scalar_one()
    
    if total_feedbacks > 0:
        fb_corr_res = await db.execute(
            select(func.count()).select_from(Feedback).where(Feedback.is_correct == False)
        )
        corrections = fb_corr_res.scalar_one()
        feedback_correction_rate = float(corrections / total_feedbacks)
    else:
        feedback_correction_rate = 0.0
        
    # 5. Model F1
    eval_res = await db.execute(
        select(EvaluationRun).order_by(EvaluationRun.created_at.desc())
    )
    latest_eval = eval_res.scalars().first()
    model_f1 = 0.0
    if latest_eval and latest_eval.metrics:
        model_f1 = float(latest_eval.metrics.get("f1_score", latest_eval.metrics.get("f1", 0.0)))
    
    # 6. Drift score
    latest_drift = await get_latest_drift(db)
    drift_score = float(latest_drift.drift_score) if latest_drift else 0.0
    
    return MetricsResponse(
        prediction_count=prediction_count,
        p95_latency=p95_latency,
        error_rate=error_rate,
        feedback_correction_rate=feedback_correction_rate,
        model_f1=model_f1,
        drift_score=drift_score
    )
