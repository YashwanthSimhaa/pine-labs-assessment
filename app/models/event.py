from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    event_type = Column(String)
    transaction_id = Column(String, ForeignKey("transactions.id"))
    merchant_id = Column(String)
    amount = Column(Float)
    currency = Column(String)
    timestamp = Column(DateTime)

    transaction = relationship("Transaction", back_populates="events")

    __table_args__ = (
        Index("idx_event_transaction", "transaction_id"),
        Index("idx_event_type", "event_type"),
        Index("idx_event_merchant", "merchant_id"),
    )