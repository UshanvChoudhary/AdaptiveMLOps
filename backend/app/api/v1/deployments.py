from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_admin_api_key
from app.schemas.deployment import DeploymentListResponse, DeploymentResponse, DeploymentCreate, HealthCheckResponse, DeploymentUpdate
from app.db.models.deployment import Deployment, HealthCheck, DeploymentStatus
from app.db.models.registry import ModelVersion
import uuid
import datetime

router = APIRouter(prefix="/deployments", tags=["deployments"])

@router.get("", response_model=DeploymentListResponse)
async def list_deployments(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    total = db.query(Deployment).count()
    deployments = db.query(Deployment).order_by(Deployment.created_at.desc()).offset(skip).limit(limit).all()
    return {"deployments": deployments, "total": total}

@router.get("/current", response_model=DeploymentResponse)
async def get_current_deployment(db: AsyncSession = Depends(get_db)):
    deployment = db.query(Deployment).filter(Deployment.status == DeploymentStatus.SUCCESS).order_by(Deployment.deployed_at.desc()).first()
    if not deployment:
        raise HTTPException(status_code=404, detail="No successful deployment found")
    return deployment

@router.post("", response_model=DeploymentResponse, dependencies=[Depends(get_admin_api_key)])
async def create_deployment(req: DeploymentCreate, db: AsyncSession = Depends(get_db)):
    model = db.query(ModelVersion).filter(ModelVersion.id == req.model_version_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found")
        
    dep = Deployment(**req.model_dump())
    db.add(dep)
    db.commit()
    db.refresh(dep)
    return dep

@router.patch("/{id}", response_model=DeploymentResponse, dependencies=[Depends(get_admin_api_key)])
async def update_deployment(id: uuid.UUID, req: DeploymentUpdate, db: AsyncSession = Depends(get_db)):
    dep = db.query(Deployment).filter(Deployment.id == id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    dep.status = req.status
    if req.health_result is not None:
        dep.health_result = req.health_result
    
    if req.status == DeploymentStatus.SUCCESS:
        dep.deployed_at = datetime.datetime.now(datetime.timezone.utc)
        
    db.commit()
    db.refresh(dep)
    return dep

@router.post("/{id}/health", response_model=HealthCheckResponse, dependencies=[Depends(get_admin_api_key)])
async def add_health_check(id: uuid.UUID, hc: dict, db: AsyncSession = Depends(get_db)):
    dep = db.query(Deployment).filter(Deployment.id == id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
        
    check = HealthCheck(
        deployment_id=id,
        endpoint=hc.get("endpoint", ""),
        status_code=str(hc.get("status_code")),
        response_time_ms=str(hc.get("response_time_ms")),
        is_healthy=bool(hc.get("is_healthy", False)),
        details=hc.get("details", "")
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check

@router.get("/{id}/health", response_model=list[HealthCheckResponse])
async def get_health_checks(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return db.query(HealthCheck).filter(HealthCheck.deployment_id == id).order_by(HealthCheck.created_at.desc()).all()
