from fastapi import APIRouter
from app.api.v1 import predictions, feedback, registry, retraining, deployments, drift, metrics, auth

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(registry.router)
api_router.include_router(retraining.router)
api_router.include_router(deployments.router)

@api_router.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok"}

@api_router.get("/ready", tags=["health"])
async def ready_check():
    return {"status": "ok"}

router = api_router
api_router.include_router(drift.router, prefix="/drift", tags=["drift"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])

from app.api.v1 import governance

api_router.include_router(governance.router, prefix="/governance", tags=["governance"])

from app.api.v1 import demo
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
