from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models.prediction import Prediction
from app.schemas.prediction import PredictionResponse

async def save_prediction(db: AsyncSession, response: PredictionResponse, input_text: str) -> Prediction:
    db_obj = Prediction(
        id=response.prediction_id,
        model_version=response.model_version,
        input_text=input_text,
        predicted_label=response.label,
        confidence=response.confidence,
        latency_ms=response.latency_ms,
        trace_id=response.request_id,
        created_at=response.created_at
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
