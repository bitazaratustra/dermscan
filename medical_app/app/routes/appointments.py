from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.appointment import Appointment
from ..models.prediction import Prediction
from ..schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentSummary
from ..utils.security import get_current_user
from ..models.user import User

router = APIRouter(tags=["Appointments"])

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    prediction = db.query(Prediction).filter_by(id=appointment.prediction_id, user_id=current_user.id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="Diagnóstico no encontrado")


    db_appointment = Appointment(
        user_id=current_user.id,
        prediction_id=appointment.prediction_id,
        scheduled_time=appointment.scheduled_time
    )

    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)

    return db_appointment


@router.get("", response_model=List[AppointmentSummary])
async def get_all_appointments(db: Session = Depends(get_db)):
    appointments = db.query(Appointment).join(Prediction).join(User).all()
    return [
        AppointmentSummary(
            id=a.id,
            scheduled_time=a.scheduled_time,
            status=a.status,
            diagnosis=a.prediction.diagnosis,
            confidence=a.prediction.confidence,
            user_full_name=a.user.full_name
        )
        for a in appointments
    ]


@router.get("/me", response_model=List[AppointmentSummary])
async def get_my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    appointments = db.query(Appointment).filter_by(user_id=current_user.id).join(Prediction).all()
    return [
        AppointmentSummary(
            id=a.id,
            scheduled_time=a.scheduled_time,
            status=a.status,
            diagnosis=a.prediction.diagnosis,
            confidence=a.prediction.confidence,
            user_full_name=None
        )
        for a in appointments
    ]
