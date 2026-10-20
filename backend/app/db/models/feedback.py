from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from app.db.session import Base
import uuid

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.id"), nullable=False, unique=True)
    user_id = Column(String(50), nullable=True) # Optional for now
    is_correct = Column(Boolean, nullable=False)
    corrected_label = Column(String(50), nullable=True)
    comments = Column(Text, nullable=True)
    feedback_status = Column(String(20), nullable=False, default="pending")
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), index=True)
