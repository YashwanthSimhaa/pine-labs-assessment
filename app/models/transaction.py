from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    merchant_id = Column(String, ForeignKey("merchants.id"))
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
    created_at = Column(DateTime)

    events = relationship("Event", back_populates="transaction")
    merchant = relationship("Merchant")

    __table_args__ = (
        Index("idx_transaction_merchant", "merchant_id"),
        Index("idx_transaction_status", "status"),
        Index("idx_transaction_created_at", "created_at"),
    )