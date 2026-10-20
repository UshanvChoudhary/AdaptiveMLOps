from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.schemas.feedback import FeedbackRequest, FeedbackResponse
from app.dependencies import get_db
from app.ml.prediction_service import prediction_service
from app.services.prediction_repository import save_prediction
from app.services.feedback_repository import save_feedback
from app.db.models.prediction import Prediction
import time
import uuid
from datetime import datetime, timezone
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
    if prediction_service is not None and (prediction_service.model is None or prediction_service.vectorizer is None):
        prediction_service.load_model()

    if prediction_service is None or prediction_service.model is None:
        raise HTTPException(status_code=503, detail="Model is currently unavailable")
        
    start_time = time.perf_counter()
    
    try:
        label, confidence, version = prediction_service.predict(prediction_req.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
        
    latency_ms = (time.perf_counter() - start_time) * 1000
    
    response = PredictionResponse(
        prediction_id=uuid.uuid4(),
        model_version=version,
        label=label,
        confidence=confidence,
        explanation=[],
        latency_ms=latency_ms,
        created_at=datetime.now(timezone.utc),
        request_id=x_request_id
    )
    
    await save_prediction(db, response, prediction_req.text)
    
    return response

@router.post("/{prediction_id}/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: Request,
    prediction_id: uuid.UUID,
    feedback_req: FeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    # Check if prediction exists
    from sqlalchemy.future import select
    pred = (await db.execute(select(Prediction).filter(Prediction.id == prediction_id))).scalars().first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
        
    if not feedback_req.is_correct and feedback_req.corrected_label:
        valid_labels = list(prediction_service.model.classes_) if prediction_service.model else []
        if feedback_req.corrected_label not in valid_labels:
            raise HTTPException(status_code=422, detail=f"corrected_label must be one of {valid_labels}")
        
    try:
        feedback = await save_feedback(db, prediction_id, feedback_req)
        return feedback
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
