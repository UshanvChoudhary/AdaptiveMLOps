from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db, get_admin_api_key
from app.schemas.registry import ModelVersionResponse, ModelVersionListResponse
from app.services.registry_service import get_all_models, get_model_by_version

router = APIRouter(prefix="/models", tags=["registry"])

@router.get("/", response_model=ModelVersionListResponse)
async def list_models(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    models = await get_all_models(db, skip=skip, limit=limit)
    total = len(models)
    return {"models": models, "total": total}

@router.get("/{version}", response_model=ModelVersionResponse)
async def get_model(version: str, db: AsyncSession = Depends(get_db)):
    model = await get_model_by_version(db, version)
    if not model:
        raise HTTPException(status_code=404, detail="Model version not found")
    return model

from app.schemas.registry import PromotionResponse, StatusUpdateResponse
from app.services.registry_service import promote_model, manual_approve_model, manual_reject_model

@router.post("/{version}/promote", response_model=PromotionResponse)
async def promote_candidate(version: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await promote_model(db, version)
        return result
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{version}/approve", response_model=StatusUpdateResponse)
async def approve_candidate(version: str, db: AsyncSession = Depends(get_db)):
    try:
        model = await manual_approve_model(db, version)
        return {"version": model.version, "status": model.status}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{version}/reject", response_model=StatusUpdateResponse)
async def reject_candidate(version: str, db: AsyncSession = Depends(get_db)):
    try:
        model = await manual_reject_model(db, version)
        return {"version": model.version, "status": model.status}
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
