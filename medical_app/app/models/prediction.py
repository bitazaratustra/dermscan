from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from .base import Base
from sqlalchemy.sql import func

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    image_path = Column(String)
    diagnosis = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
