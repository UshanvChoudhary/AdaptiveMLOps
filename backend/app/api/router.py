from fastapi import APIRouter
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
    return {"status": "ok"}

@api_router.get("/ready", tags=["health"])
async def ready_check():
    return {"status": "ok"}

router = api_router
