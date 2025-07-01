from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_id = Column(Integer, ForeignKey("predictions.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String, default="pendiente")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True)
    image_filename = Column(String, nullable=True)

    user = relationship("User", back_populates="appointments")
    prediction = relationship("Prediction", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
