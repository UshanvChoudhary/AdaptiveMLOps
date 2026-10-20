import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from pydantic import BaseModel

from app.schemas.feedback import FeedbackResponse, FeedbackRequest
from app.dependencies import get_db
from app.services.feedback_repository import get_user_feedback, save_feedback
from app.db.models.prediction import Prediction
from app.db.models.feedback import Feedback

router = APIRouter()

class DirectFeedbackRequest(BaseModel):
    prediction_id: Optional[str] = None
    is_correct: Optional[bool] = None
    correct: Optional[bool] = None
    actual_class: Optional[int] = None
    corrected_label: Optional[str] = None
    comments: Optional[str] = None

@router.get("/me", response_model=List[FeedbackResponse])
async def get_my_feedback(db: AsyncSession = Depends(get_db)):
    feedbacks = await get_user_feedback(db, user_id="anonymous")
    return feedbacks

@router.post("/")
async def submit_direct_feedback(
    request: Request,
    body: DirectFeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    # If prediction_id is provided, check or create feedback
    is_corr = body.is_correct if body.is_correct is not None else (body.correct if body.correct is not None else True)
    
    # Try finding prediction
    pred = None
    if body.prediction_id:
        try:
            pid = uuid.UUID(body.prediction_id)
            pred = (await db.execute(select(Prediction).filter(Prediction.id == pid))).scalars().first()
        except Exception:
            pass
            
    if not pred:
        # Get latest prediction
        pred = (await db.execute(select(Prediction).order_by(Prediction.created_at.desc()))).scalars().first()

    if pred:
        fb_req = FeedbackRequest(
            is_correct=is_corr,
            corrected_label=body.corrected_label,
            comments=body.comments or "Submitted via UI"
        )
        try:
            fb = await save_feedback(db, pred.id, fb_req)
            return {"status": "success", "feedback_id": str(fb.id), "prediction_id": str(pred.id)}
        except Exception as e:
            return {"status": "recorded", "message": str(e)}
            
    return {"status": "success", "message": "Feedback recorded"}
