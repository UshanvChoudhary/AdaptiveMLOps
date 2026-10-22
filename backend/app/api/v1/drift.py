from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
from app.dependencies import get_db
from app.schemas.monitoring import DriftRunResponse
from app.services.drift_service import calculate_drift, get_latest_drift

router = APIRouter()

class DriftRunRequest(BaseModel):
    reference_dataset_id: Optional[str] = None

@router.post("/run", response_model=DriftRunResponse)
async def run_drift_analysis(request: DriftRunRequest, db: AsyncSession = Depends(get_db)):
    drift_run = await calculate_drift(db, reference_dataset_id=request.reference_dataset_id)
    return drift_run

@router.get("/latest", response_model=DriftRunResponse)
async def get_latest_drift_endpoint(db: AsyncSession = Depends(get_db)):
    drift_run = await get_latest_drift(db)
    if not drift_run:
        raise HTTPException(status_code=404, detail="No drift runs found")
    return drift_run
