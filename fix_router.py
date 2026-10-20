import sys

file_path = 'backend/app/api/router.py'
with open(file_path, 'r') as f:
    content = f.read()

replacement = '''from fastapi import APIRouter
from app.api.v1 import predictions, feedback, registry, retraining

api_router = APIRouter()
api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(registry.router)
api_router.include_router(retraining.router)

@api_router.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}

@api_router.get("/ready", tags=["health"])
def ready_check():
    return {"status": "ok"}

router = api_router'''

with open(file_path, 'w') as f:
    f.write(replacement)
