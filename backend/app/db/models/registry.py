from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text
from app.db.session import Base
import uuid

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(String(50), nullable=False, unique=True, index=True)
    checksum = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), index=True)

class TrainingRun(Base):
    __tablename__ = "training_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)
    git_commit = Column(String(40), nullable=False)
    hyperparameters = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), index=True)
    
    dataset = relationship("Dataset")

class ModelVersion(Base):
    __tablename__ = "model_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(String(50), nullable=False, unique=True, index=True)
    algorithm = Column(String(100), nullable=False)
    training_run_id = Column(UUID(as_uuid=True), ForeignKey("training_runs.id"), nullable=False, index=True)
    artifact_path = Column(String(255), nullable=False)
    status = Column(String(20), nullable=False, default="CANDIDATE")
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), index=True)
    
    training_run = relationship("TrainingRun")
    evaluations = relationship("EvaluationRun", back_populates="model_version")

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False, index=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False, index=True)
    metrics = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), index=True)
    
    model_version = relationship("ModelVersion", back_populates="evaluations")

    @property
    def dataset(self):
        return self.training_run.dataset if self.training_run else None

class ModelAudit(Base):
    __tablename__ = "model_audits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False) # e.g. PROMOTE, REJECT, APPROVE
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), index=True)
