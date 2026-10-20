from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from app.db.session import Base
import uuid

class RetrainingJob(Base):
    __tablename__ = "retraining_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trigger_type = Column(String(50), nullable=False)
    reason = Column(Text, nullable=True)
    feedback_count = Column(Integer, nullable=False, default=0)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=True, index=True)
    candidate_model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=True, index=True)
    status = Column(String(20), nullable=False, default="QUEUED")
    error_message = Column(Text, nullable=True)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), index=True)
