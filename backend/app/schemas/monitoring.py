from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.db.models.monitoring import DriftStatus

class DriftRunResponse(BaseModel):
    id: uuid.UUID
    drift_score: float
    status: DriftStatus
    reference_dataset_id: Optional[str]
    current_window_start: Optional[datetime]
    current_window_end: Optional[datetime]
    class_distribution: Optional[Dict[str, Any]]
    confidence_trend: Optional[Dict[str, Any]]
    input_distribution: Optional[Dict[str, Any]]
    recommended_action: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MetricsResponse(BaseModel):
    prediction_count: int
    p95_latency: float
    error_rate: float
    feedback_correction_rate: float
    model_f1: float
    drift_score: float
