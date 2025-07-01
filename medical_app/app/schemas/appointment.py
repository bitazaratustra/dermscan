from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class AppointmentCreate(BaseModel):
    prediction_id: int
    scheduled_time: datetime

class AppointmentResponse(BaseModel):
    id: int
    prediction_id: int
    scheduled_time: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class AppointmentSummary(BaseModel):
    id: int
    scheduled_time: datetime
    status: str
    diagnosis: str
    confidence: float
    user_full_name: str
    image_filename: Optional[str] = None
    class Config:
        orm_mode = True
class AppointmentStatusUpdate(BaseModel):
    status: str
