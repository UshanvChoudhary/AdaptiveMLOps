from enum import Enum
from pydantic import BaseModel

class IntentEnum(str, Enum):
    billing = "billing"
    technical_support = "technical_support"
    refund = "refund"
    account_management = "account_management"

class TicketData(BaseModel):
    text: str
    intent: IntentEnum
