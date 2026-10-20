from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.feedback import FeedbackResponse
from app.dependencies import get_db
from app.services.feedback_repository import get_user_feedback

router = APIRouter()

@router.get("/me", response_model=List[FeedbackResponse])
async def get_my_feedback(db: AsyncSession = Depends(get_db)):
    # For now, just return for anonymous user
    feedbacks = await get_user_feedback(db, user_id="anonymous")
    return feedbacks
