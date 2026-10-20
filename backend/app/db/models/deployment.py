from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
from sqlalchemy.sql import func
import uuid
import enum
from sqlalchemy.orm import relationship

class DeploymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False, index=True)
    image_tag = Column(String, nullable=False)
    environment = Column(String, nullable=False)
    status = Column(String, default=DeploymentStatus.PENDING)
    actor = Column(String, nullable=True)
    health_result = Column(JSON, nullable=True)
    model_version = relationship("ModelVersion")
    deployed_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HealthCheck(Base):
    __tablename__ = "health_checks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    deployment_id = Column(UUID(as_uuid=True), ForeignKey("deployments.id"), nullable=False, index=True)
    endpoint = Column(String, nullable=False)
    status_code = Column(String, nullable=True)
    response_time_ms = Column(String, nullable=True)
    is_healthy = Column(Boolean, nullable=False, default=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
