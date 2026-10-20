import os
import uuid
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.dependencies import get_db, get_current_user, get_current_admin_or_api_key, get_current_reviewer_or_api_key
from app.db.models.governance import Approval, AuditLog, ApprovalStatus, AuditAction
from app.db.models.registry import ModelVersion
from app.db.models.deployment import Deployment, DeploymentStatus
from app.schemas.governance import (
    ApprovalCreate, ApprovalResponse, ApprovalUpdate,
    AuditLogResponse, RollbackRequest
)
from app.ml.prediction_service import prediction_service

router = APIRouter()

@router.get("/approvals", response_model=List[ApprovalResponse])
async def get_approvals(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_reviewer_or_api_key)
):
    result = await db.execute(select(Approval).order_by(Approval.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/approvals", response_model=ApprovalResponse)
async def create_approval(
    approval_in: ApprovalCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: Any = Depends(get_current_reviewer_or_api_key)
):
    model_res = await db.execute(select(ModelVersion).where(ModelVersion.id == uuid.UUID(approval_in.model_version_id)))
    model = model_res.scalars().first()
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found")

    actor_name = current_user.get("username", "reviewer") if isinstance(current_user, dict) else "reviewer"

    approval = Approval(
        id=uuid.uuid4(),
        model_version_id=approval_in.model_version_id,
        status=approval_in.status,
        reviewer=actor_name,
        comments=approval_in.comments
    )
    db.add(approval)
    
    action = AuditAction.MODEL_APPROVED if approval_in.status == ApprovalStatus.APPROVED else AuditAction.MODEL_REJECTED
    audit = AuditLog(
        id=uuid.uuid4(),
        action=action,
        actor=actor_name,
        resource_id=approval_in.model_version_id,
        resource_type="model_version",
        details=approval_in.comments
    )
    db.add(audit)
    await db.commit()
    await db.refresh(approval)
    return approval

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_admin_or_api_key)
):
    result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/models/{version}/rollback")
async def rollback_model(
    version: str,
    request: RollbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_admin_or_api_key)
):
    actor_name = current_user.get("username", "admin") if isinstance(current_user, dict) else "admin"

    current_res = await db.execute(select(ModelVersion).where(ModelVersion.version == version))
    current_model = current_res.scalars().first()
    if not current_model:
        raise HTTPException(status_code=404, detail="Current model version not found")

    # Find previous healthy deployment
    prev_res = await db.execute(
        select(Deployment)
        .where(
            Deployment.status == DeploymentStatus.SUCCESS,
            Deployment.model_version_id != current_model.id
        )
        .order_by(Deployment.created_at.desc())
    )
    previous_deployment = prev_res.scalars().first()
    if not previous_deployment:
        raise HTTPException(status_code=400, detail="No previous healthy deployment found to rollback to")

    prev_model_res = await db.execute(select(ModelVersion).where(ModelVersion.id == previous_deployment.model_version_id))
    previous_model = prev_model_res.scalars().first()
    if not previous_model:
        raise HTTPException(status_code=404, detail="Previous model version not found")
    
    # Verify artifact exists on disk before rollback
    target_artifact_dir = previous_model.artifact_path
    if not os.path.isabs(target_artifact_dir):
        from app.config import settings
        target_artifact_dir = os.path.join(settings.BASE_DIR, target_artifact_dir)

    if not os.path.exists(target_artifact_dir):
        raise HTTPException(
            status_code=500,
            detail=f"Previous model artifact path '{previous_model.artifact_path}' does not exist on disk"
        )

    # Restore in-memory active prediction service model
    try:
        prediction_service.artifact_dir = target_artifact_dir
        prediction_service.load_model()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reload previous model artifact: {str(e)}"
        )

    # Update database statuses
    current_model.status = "ARCHIVED"
    previous_model.status = "PRODUCTION"

    new_deployment = Deployment(
        id=uuid.uuid4(),
        model_version_id=previous_model.id,
        image_tag=f"adaptive-model:{previous_model.version}",
        environment="production",
        status=DeploymentStatus.SUCCESS,
        actor=actor_name,
        health_result={"status": "Rollback healthy and verified"}
    )
    db.add(new_deployment)
    
    audit = AuditLog(
        id=uuid.uuid4(),
        action=AuditAction.ROLLBACK,
        actor=actor_name,
        resource_id=previous_model.id,
        resource_type="model_version",
        details=f"Rolled back from {version} to {previous_model.version}. Reason: {request.reason}"
    )
    db.add(audit)
    
    await db.commit()
    return {
        "status": "success",
        "rolled_back_to": previous_model.version,
        "artifact_restored": target_artifact_dir
    }
