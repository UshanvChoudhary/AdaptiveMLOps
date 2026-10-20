from pydantic import BaseModel, UUID4, ConfigDict
from datetime import datetime
from typing import Optional, List

class RetrainingTriggerRequest(BaseModel):
    trigger_type: str  # MANUAL, FEEDBACK_THRESHOLD
    reason: Optional[str] = None

class RetrainingJobResponse(BaseModel):
    id: UUID4
    trigger_type: str
    reason: Optional[str]
    feedback_count: int
    dataset_id: Optional[UUID4]
    candidate_model_version_id: Optional[UUID4]
    status: str
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RetrainingJobListResponse(BaseModel):
    jobs: List[RetrainingJobResponse]
    total: int = 0
