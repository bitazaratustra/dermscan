from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..utils.security import get_current_user
from ..schemas.prediction import PredictionResponse
from ..models.prediction import Prediction

router = APIRouter()

@router.get("/", response_model=List[PredictionResponse])
async def get_user_predictions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .all()
    )
