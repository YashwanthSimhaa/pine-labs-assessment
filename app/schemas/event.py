from pydantic import BaseModel
from datetime import datetime

class EventCreate(BaseModel, extra="forbid"):
    event_id: str
    event_type: str
    transaction_id: str
    merchant_id: str
    merchant_name: str
    amount: float
    currency: str
    timestamp: datetime