from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.dependencies import get_db, get_current_admin_or_api_key
from app.schemas.deployment import DeploymentListResponse, DeploymentResponse, DeploymentCreate, HealthCheckResponse, DeploymentUpdate
from app.db.models.deployment import Deployment, HealthCheck, DeploymentStatus
from app.db.models.registry import ModelVersion
import uuid
import datetime

router = APIRouter(prefix="/deployments", tags=["deployments"])

@router.get("", response_model=DeploymentListResponse)
async def list_deployments(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    count_res = await db.execute(select(func.count()).select_from(Deployment))
    total = count_res.scalar_one()
    
    dep_res = await db.execute(
        select(Deployment).order_by(Deployment.created_at.desc()).offset(skip).limit(limit)
    )
    deployments = dep_res.scalars().all()
    return {"deployments": deployments, "total": total}

@router.get("/current", response_model=DeploymentResponse)
async def get_current_deployment(db: AsyncSession = Depends(get_db)):
    dep_res = await db.execute(
        select(Deployment)
        .where(Deployment.status == DeploymentStatus.SUCCESS)
        .order_by(Deployment.deployed_at.desc())
    )
    deployment = dep_res.scalars().first()
    if not deployment:
        raise HTTPException(status_code=404, detail="No successful deployment found")
    return deployment

@router.post("", response_model=DeploymentResponse, dependencies=[Depends(get_current_admin_or_api_key)])
async def create_deployment(req: DeploymentCreate, db: AsyncSession = Depends(get_db)):
    m_res = await db.execute(select(ModelVersion).where(ModelVersion.id == req.model_version_id))
    model = m_res.scalars().first()
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found")
        
    dep = Deployment(**req.model_dump())
    db.add(dep)
    await db.commit()
    await db.refresh(dep)
    return dep

@router.patch("/{id}", response_model=DeploymentResponse, dependencies=[Depends(get_current_admin_or_api_key)])
async def update_deployment(id: uuid.UUID, req: DeploymentUpdate, db: AsyncSession = Depends(get_db)):
    d_res = await db.execute(select(Deployment).where(Deployment.id == id))
    dep = d_res.scalars().first()
    if not dep:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    dep.status = req.status
    if req.health_result is not None:
        dep.health_result = req.health_result
    
    if req.status == DeploymentStatus.SUCCESS:
        dep.deployed_at = datetime.datetime.now(datetime.timezone.utc)
        
    await db.commit()
    await db.refresh(dep)
    return dep

@router.post("/{id}/health", response_model=HealthCheckResponse, dependencies=[Depends(get_current_admin_or_api_key)])
async def add_health_check(id: uuid.UUID, hc: dict, db: AsyncSession = Depends(get_db)):
    d_res = await db.execute(select(Deployment).where(Deployment.id == id))
    dep = d_res.scalars().first()
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
    await db.commit()
    await db.refresh(check)
    return check

@router.get("/{id}/health", response_model=list[HealthCheckResponse])
async def get_health_checks(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    res = await db.execute(
        select(HealthCheck).where(HealthCheck.deployment_id == id).order_by(HealthCheck.created_at.desc())
    )
    return res.scalars().all()
