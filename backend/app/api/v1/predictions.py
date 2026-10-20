import time
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.dependencies import get_db
from app.ml.prediction_service import prediction_service
from app.services.prediction_repository import save_prediction
from app.services.feedback_repository import save_feedback
from app.db.models.prediction import Prediction
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/", response_model=PredictionResponse)
async def create_prediction(
    request: Request,
    prediction_req: PredictionRequest,
    db: AsyncSession = Depends(get_db),
    x_request_id: uuid.UUID = Header(default_factory=uuid.uuid4)
):
    if prediction_service is None:
        raise HTTPException(status_code=503, detail="Prediction service unavailable")
        
    if prediction_service.model is None:
        prediction_service.load_model()
        
    if prediction_service.model is None:
        raise HTTPException(status_code=503, detail="Model is currently unavailable")
        
    # Determine text from request
    query_text = prediction_req.text
    if not query_text and prediction_req.features:
        query_text = " ".join(f"{k} {v}" for k, v in prediction_req.features.items())
    if not query_text:
        query_text = "General inquiry sample transaction"
        
    start_time = time.perf_counter()
    
    try:
        label, confidence, version = prediction_service.predict(query_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
        
    latency_ms = (time.perf_counter() - start_time) * 1000
    
    response = PredictionResponse(
        prediction_id=uuid.uuid4(),
        model_version=version,
        label=str(label),
        confidence=float(confidence),
        explanation=[f"Classified as '{label}' with {float(confidence)*100:.1f}% confidence"],
        latency_ms=float(latency_ms),
        created_at=datetime.now(timezone.utc),
        request_id=x_request_id
    )
    
    await save_prediction(db, response, query_text)
    
    return response

@router.post("/{prediction_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: Request,
    prediction_id: uuid.UUID,
    feedback_req: FeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    pred = (await db.execute(select(Prediction).filter(Prediction.id == prediction_id))).scalars().first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
        
    try:
        feedback = await save_feedback(db, prediction_id, feedback_req)
        return feedback
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
