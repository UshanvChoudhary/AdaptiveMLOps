from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.monitoring import DriftRun, DriftStatus
from app.db.models.prediction import Prediction
from app.config import settings
from datetime import datetime, timedelta
import collections
from typing import Optional
from sqlalchemy import func

async def calculate_drift(db: AsyncSession, reference_dataset_id: Optional[str] = None) -> DriftRun:
    now = datetime.utcnow()
    # Simple window: last 24 hours vs previous 24 hours (if no reference provided)
    # Since this is a practical student project, we will use a time-based window
    # to compare predictions.
    
    current_window_start = now - timedelta(days=1)
    
    # 1. Fetch recent predictions
    recent_preds = (await db.execute(select(Prediction).filter(Prediction.created_at >= current_window_start).order_by(Prediction.created_at.desc()).limit(1000))).scalars().all()
    
    # Calculate distributions
    class_counts = collections.Counter([p.predicted_label for p in recent_preds])
    total = len(recent_preds)
    
    class_distribution = {}
    confidence_trend = {"mean": 0.0, "min": 0.0, "max": 0.0}
    input_distribution = {"avg_length": 0.0}
    
    drift_score = 0.0
    status = DriftStatus.NORMAL
    recommended_action = "No action required."
    
    if total > 0:
        for k, v in class_counts.items():
            class_distribution[str(k)] = v / total
            
        confidences = [p.confidence for p in recent_preds if p.confidence is not None]
        if confidences:
            confidence_trend["mean"] = sum(confidences) / len(confidences)
            confidence_trend["min"] = min(confidences)
            confidence_trend["max"] = max(confidences)
            
        lengths = [len(str(p.input_text)) for p in recent_preds]
        if lengths:
            input_distribution["avg_length"] = sum(lengths) / len(lengths)
            
        # Very simple drift simulation or calculation.
        # In a real scenario, we'd compare `class_distribution` to `reference_dataset`'s class distribution.
        # Here we'll simulate a drift score based on confidence drop and class imbalance for demonstration,
        # or compare to a baseline if we had one.
        # Let's say if mean confidence < 0.7, that adds to drift.
        confidence_penalty = max(0.0, 0.85 - confidence_trend["mean"])
        
        # If one class dominates more than 90%, it's drifting (assuming balanced training)
        max_class_prop = max(class_distribution.values()) if class_distribution else 0.0
        imbalance_penalty = max(0.0, max_class_prop - 0.7)
        
        drift_score = confidence_penalty + imbalance_penalty
        
    if drift_score >= settings.DRIFT_THRESHOLD_CRITICAL:
        status = DriftStatus.CRITICAL
        recommended_action = "Trigger Retraining Pipeline immediately."
    elif drift_score >= settings.DRIFT_THRESHOLD_WARNING:
        status = DriftStatus.WARNING
        recommended_action = "Monitor closely; collect more ground truth."
        
    drift_run = DriftRun(
        drift_score=drift_score,
        status=status,
        reference_dataset_id=reference_dataset_id,
        current_window_start=current_window_start,
        current_window_end=now,
        class_distribution=class_distribution,
        confidence_trend=confidence_trend,
        input_distribution=input_distribution,
        recommended_action=recommended_action
    )
    
    db.add(drift_run)
    await db.commit()
    await db.refresh(drift_run)
    
    return drift_run

async def get_latest_drift(db: AsyncSession) -> Optional[DriftRun]:
    return (await db.execute(select(DriftRun).order_by(DriftRun.created_at.desc()))).scalars().first()
