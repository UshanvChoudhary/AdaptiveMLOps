import uuid
from sqlalchemy import Column, String, Float, DateTime, JSON, Enum
import sqlalchemy as sa
from sqlalchemy.sql import func
import enum
from app.db.session import Base

class DriftStatus(str, enum.Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

class DriftRun(Base):
    __tablename__ = "drift_runs"

    id = Column(sa.UUID(), primary_key=True, default=uuid.uuid4, index=True)
    drift_score = Column(Float, nullable=False)
    status = Column(sa.Enum(DriftStatus, name="drift_status_enum", create_constraint=False), nullable=False)
    reference_dataset_id = Column(String, nullable=True)
    current_window_start = Column(DateTime(timezone=True), nullable=True)
    current_window_end = Column(DateTime(timezone=True), nullable=True)
    
    class_distribution = Column(JSON, nullable=True)
    confidence_trend = Column(JSON, nullable=True)
    input_distribution = Column(JSON, nullable=True)
    
    recommended_action = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
