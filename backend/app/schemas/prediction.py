from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import List, Optional, Any, Dict

class PredictionRequest(BaseModel):
    text: Optional[str] = Field(None, max_length=5000)
    features: Optional[Dict[str, Any]] = None

class PredictionResponse(BaseModel):
    prediction_id: UUID4
    model_version: str
    label: str
    confidence: float
    explanation: List[str] = Field(default_factory=list)
    latency_ms: float
    created_at: datetime
    request_id: UUID4
