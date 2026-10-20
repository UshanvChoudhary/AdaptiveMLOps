from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime
import uuid
from app.db.models.deployment import DeploymentStatus

class HealthCheckBase(BaseModel):
    endpoint: str
    status_code: Optional[str] = None
    response_time_ms: Optional[str] = None
    is_healthy: bool
    details: Optional[str] = None

class HealthCheckResponse(HealthCheckBase):
    id: uuid.UUID
    deployment_id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DeploymentBase(BaseModel):
    model_version_id: uuid.UUID
    image_tag: str
    environment: str
    actor: Optional[str] = None

class DeploymentCreate(DeploymentBase):
    pass

class DeploymentUpdate(BaseModel):
    status: DeploymentStatus
    health_result: Optional[Dict[str, Any]] = None

class DeploymentResponse(DeploymentBase):
    id: uuid.UUID
    status: DeploymentStatus
    health_result: Optional[Dict[str, Any]] = None
    deployed_at: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DeploymentListResponse(BaseModel):
    deployments: List[DeploymentResponse]
    total: int
