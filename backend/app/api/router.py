from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.dependencies import get_db
from app.ml.prediction_service import prediction_service
from app.api.v1 import predictions, feedback, registry, retraining, deployments, drift, metrics, auth, governance, demo

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(predictions.router, prefix="/predict", tags=["predict_alias"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(registry.router)
api_router.include_router(retraining.router)
api_router.include_router(deployments.router)
api_router.include_router(drift.router, prefix="/drift", tags=["drift"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(governance.router, prefix="/governance", tags=["governance"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])

@api_router.get("/health", tags=["health"])
async def health_check():
    """Liveness probe: verifies process is alive."""
    return {"status": "ok"}

@api_router.get("/ready", tags=["health"])
async def ready_check(db: AsyncSession = Depends(get_db)):
    """Readiness probe: verifies essential dependencies (Database and ML Model)."""
    # 1. Verify Database connectivity
    try:
        await db.execute(select(1))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {str(e)}"
        )
        
    # 2. Verify ML Model availability
    if prediction_service is None or getattr(prediction_service, 'model', None) is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Production model is not loaded or unavailable"
        )
        
    return {
        "status": "ready",
        "database": "connected",
        "model": "loaded",
        "model_version": getattr(prediction_service, 'model_version', '1.0.0')
    }

router = api_router
