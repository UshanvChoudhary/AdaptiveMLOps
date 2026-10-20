from pydantic import BaseModel, ConfigDict
from typing import Optional, Union
from uuid import UUID
from datetime import datetime
from app.db.models.governance import ApprovalStatus, AuditAction

class ApprovalBase(BaseModel):
    model_version_id: Union[UUID, str]
    status: ApprovalStatus
    comments: Optional[str] = None

class ApprovalCreate(ApprovalBase):
    pass

class ApprovalUpdate(BaseModel):
    status: ApprovalStatus
    comments: Optional[str] = None

class ApprovalResponse(ApprovalBase):
    id: Union[UUID, str]
    reviewer: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AuditLogBase(BaseModel):
    action: AuditAction
    resource_id: Optional[Union[UUID, str]] = None
    resource_type: Optional[str] = None
    details: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    actor: str

class AuditLogResponse(AuditLogBase):
    id: Union[UUID, str]
    actor: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RollbackRequest(BaseModel):
    reason: Optional[str] = None
