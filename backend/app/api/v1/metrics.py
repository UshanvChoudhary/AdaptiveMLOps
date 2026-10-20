from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from app.dependencies import get_db
from app.schemas.monitoring import MetricsResponse
from app.db.models.prediction import Prediction
from app.db.models.feedback import Feedback
from app.db.models.registry import EvaluationRun
from app.services.drift_service import get_latest_drift
import datetime

router = APIRouter()

@router.get("/", response_model=MetricsResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    # 1. Prediction count
    prediction_count = db.query(Prediction).count()
    
    # 2. p95 latency & 3. Error rate
    # Fetch only the last 1000 predictions to bound memory footprint while getting a recent estimate
    recent_latencies = db.query(Prediction.latency_ms).filter(Prediction.latency_ms.isnot(None)).order_by(Prediction.created_at.desc()).limit(1000).all()
    latencies = [r[0] for r in recent_latencies]
    
    p95_latency = 0.0
    error_rate = 0.0
    
    if latencies:
        latencies.sort()
        idx = int(len(latencies) * 0.95)
        p95_latency = latencies[idx]
        error_count = sum(1 for l in latencies if l > 500)
        error_rate = error_count / len(latencies)
    
    # 4. Feedback correction rate
    total_feedbacks = db.query(Feedback).count()
    if total_feedbacks > 0:
        corrections = db.query(Feedback).filter(Feedback.is_correct == False).count()
        feedback_correction_rate = corrections / total_feedbacks
    else:
        feedback_correction_rate = 0.0
        
    # 5. Model F1
    latest_eval = db.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).first()
    model_f1 = latest_eval.f1_score if latest_eval else 0.0
    
    # 6. Drift score
    latest_drift = get_latest_drift(db)
    drift_score = latest_drift.drift_score if latest_drift else 0.0
    
    return MetricsResponse(
        prediction_count=prediction_count,
        p95_latency=p95_latency,
        error_rate=error_rate,
        feedback_correction_rate=feedback_correction_rate,
        model_f1=model_f1,
        drift_score=drift_score
    )
