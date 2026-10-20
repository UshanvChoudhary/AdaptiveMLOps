from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.db.models.feedback import Feedback
from app.schemas.feedback import FeedbackRequest
from uuid import UUID

async def save_feedback(db: AsyncSession, prediction_id: UUID, req: FeedbackRequest, user_id: str = "anonymous"):
    db_feedback = Feedback(
        prediction_id=prediction_id,
        user_id=user_id,
        is_correct=req.is_correct,
        corrected_label=req.corrected_label,
        comments=req.comments,
        feedback_status="pending"
    )
    
    try:
        db.add(db_feedback)
        await db.commit()
        await db.refresh(db_feedback)
        return db_feedback
    except IntegrityError:
        await db.rollback()
        raise ValueError("Feedback already exists for this prediction")

async def get_user_feedback(db: AsyncSession, user_id: str = "anonymous"):
    return (await db.execute(select(Feedback).filter(Feedback.user_id == user_id))).scalars().all()
