from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from app.db.models.governance import ApprovalStatus, AuditAction

class ApprovalBase(BaseModel):
    model_version_id: str
    status: ApprovalStatus
    comments: Optional[str] = None

class ApprovalCreate(ApprovalBase):
    pass

class ApprovalUpdate(BaseModel):
    status: ApprovalStatus
    comments: Optional[str] = None

class ApprovalResponse(ApprovalBase):
    id: str
    reviewer: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AuditLogBase(BaseModel):
    action: AuditAction
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    details: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    actor: str

class AuditLogResponse(AuditLogBase):
    id: str
    actor: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RollbackRequest(BaseModel):
    reason: Optional[str] = None
