from pydantic import BaseModel, UUID4, ConfigDict
from datetime import datetime
from typing import Any, Dict, Optional, List

class DatasetResponse(BaseModel):
    id: UUID4
    version: str
    checksum: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TrainingRunResponse(BaseModel):
    id: UUID4
    dataset_id: UUID4
    git_commit: str
    hyperparameters: Dict[str, Any]
    status: str
    created_at: datetime
    
    dataset: Optional[DatasetResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

class EvaluationRunResponse(BaseModel):
    id: UUID4
    model_version_id: UUID4
    dataset_id: UUID4
    metrics: Dict[str, Any]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ModelVersionResponse(BaseModel):
    id: UUID4
    version: str
    algorithm: str
    training_run_id: UUID4
    artifact_path: str
    status: str
    created_at: datetime
    
    # Nested fields for the frontend
    training_run: Optional[TrainingRunResponse] = None
    evaluations: List[EvaluationRunResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class ModelVersionListResponse(BaseModel):
    models: List[ModelVersionResponse]
    total: int = 0

class PromotionResponse(BaseModel):
    decision: str
    reason: str
    candidate_version: str
    champion_version: Optional[str] = None
    
class StatusUpdateResponse(BaseModel):
    version: str
    status: str
