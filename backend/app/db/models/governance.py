from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, UTC
import enum
import uuid

from app.db.session import Base

class ApprovalStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class AuditAction(str, enum.Enum):
    LOGIN = "LOGIN"
    PREDICTION = "PREDICTION"
    FEEDBACK_SUBMITTED = "FEEDBACK_SUBMITTED"
    RETRAINING_TRIGGERED = "RETRAINING_TRIGGERED"
    TRAINING_COMPLETED = "TRAINING_COMPLETED"
    MODEL_APPROVED = "MODEL_APPROVED"
    MODEL_REJECTED = "MODEL_REJECTED"
    DEPLOYMENT_STARTED = "DEPLOYMENT_STARTED"
    DEPLOYMENT_SUCCEEDED = "DEPLOYMENT_SUCCEEDED"
    DEPLOYMENT_FAILED = "DEPLOYMENT_FAILED"
    ROLLBACK = "ROLLBACK"

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False, index=True)
    status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    reviewer = Column(String, nullable=True) # User ID/Role
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    model_version = relationship("ModelVersion", backref="approvals")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    action = Column(Enum(AuditAction), nullable=False)
    actor = Column(String, nullable=False) # User ID/Role
    resource_id = Column(UUID(as_uuid=True), nullable=True) # Related to prediction_id, model_version_id, deployment_id, etc.
    resource_type = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
