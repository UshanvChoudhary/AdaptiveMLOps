from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import List, Optional

class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

class PredictionResponse(BaseModel):
    prediction_id: UUID4
    model_version: str
    label: str
    confidence: float
    explanation: List[str] = Field(default_factory=list)
    latency_ms: float
    created_at: datetime
    request_id: UUID4
