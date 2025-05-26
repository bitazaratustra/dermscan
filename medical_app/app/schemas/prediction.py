from pydantic import BaseModel
from datetime import datetime

class PredictionBase(BaseModel):
    image_path: str
    diagnosis: str
    confidence: float

class PredictionCreate(PredictionBase):
    pass

class PredictionResponse(PredictionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
