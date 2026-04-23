from sqlalchemy import Column, String
from app.core.database import Base

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)