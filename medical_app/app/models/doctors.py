from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    specialty = Column(String, nullable=True)
    license_number = Column(String, unique=True, nullable=False)
    hospital_affiliation = Column(String, nullable=True)

    appointments = relationship("Appointment", back_populates="doctor")
