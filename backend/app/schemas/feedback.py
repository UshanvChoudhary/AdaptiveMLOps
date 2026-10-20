from pydantic import BaseModel, ConfigDict, model_validator
from typing import Optional
from uuid import UUID
from datetime import datetime

class FeedbackRequest(BaseModel):
    is_correct: bool
    corrected_label: Optional[str] = None
    comments: Optional[str] = None
    
    @model_validator(mode="after")
    def validate_corrected_label(self) -> "FeedbackRequest":
        if not self.is_correct and not self.corrected_label:
            raise ValueError("corrected_label is mandatory when is_correct is false")
        if not self.is_correct and self.corrected_label:
            valid_labels = {"billing", "technical_support", "refund", "account_management"}
            if self.corrected_label not in valid_labels:
                raise ValueError(f"corrected_label must be one of {valid_labels}")
        return self

class FeedbackResponse(BaseModel):
    id: UUID
    prediction_id: UUID
    user_id: Optional[str]
    is_correct: bool
    corrected_label: Optional[str]
    comments: Optional[str]
    feedback_status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
