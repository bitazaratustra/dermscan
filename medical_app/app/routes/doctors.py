
from ..schemas.doctors import DoctorCreate, DoctorResponse, DoctorLogin
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel  # Agregar importación

from ..database import get_db
from ..models.doctors import Doctor
from ..models.appointment import Appointment
from ..models.prediction import Prediction
from ..models.user import User
from ..schemas.doctors import DoctorCreate, DoctorResponse
from ..schemas.appointment import AppointmentResponse, AppointmentStatusUpdate, AppointmentSummary
from ..utils.security import get_password_hash, create_access_token, get_current_doctor, verify_password, pwd_context

router = APIRouter(tags=["Doctors"])


@router.post("/register", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def register_doctor(
    doctor_data: DoctorCreate,
    db: Session = Depends(get_db)
):
    existing_doctor = db.query(Doctor).filter(Doctor.email == doctor_data.email).first()
    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    existing_license = db.query(Doctor).filter(Doctor.license_number == doctor_data.license_number).first()
    if existing_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="License number already registered"
        )

    hashed_password = get_password_hash(doctor_data.password)
    db_doctor = Doctor(
        email=doctor_data.email,
        hashed_password=hashed_password,
        full_name=doctor_data.full_name,
        specialty=doctor_data.specialty,
        license_number=doctor_data.license_number,
        hospital_affiliation=doctor_data.hospital_affiliation
    )

    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


@router.post("/login", response_model=dict)
async def login_doctor(
    login_data: DoctorLogin,
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.email == login_data.email).first()
    if not doctor or not verify_password(login_data.password, doctor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    access_token = create_access_token(
        data={"sub": doctor.email, "role": "doctor"},
        expires_delta=timedelta(minutes=1440)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": "doctor"
    }

@router.get("/me", response_model=DoctorResponse)
async def get_current_doctor_profile(
    current_doctor: Doctor = Depends(get_current_doctor)
):
    return current_doctor

@router.get("/appointments", response_model=List[AppointmentSummary])
async def get_doctor_appointments(
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    appointments = (
        db.query(Appointment)
        .filter(Appointment.doctor_id == current_doctor.id)
        .join(Prediction)
        .join(User)
        .all()
    )

    return [
        AppointmentSummary(
            id=a.id,
            scheduled_time=a.scheduled_time,
            status=a.status,
            diagnosis=a.prediction.diagnosis,
            confidence=a.prediction.confidence,
            user_full_name=a.user.full_name,
            image_filename=a.prediction.image_filename
        )
        for a in appointments
    ]

@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: int,
    status_update: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_doctor: Doctor = Depends(get_current_doctor)
):
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id,
        Appointment.doctor_id == current_doctor.id
    ).first()

    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    valid_statuses = ["pendiente", "confirmada", "cancelada", "completada"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Valid options: {', '.join(valid_statuses)}"
        )

    appointment.status = status_update.status
    db.commit()
    db.refresh(appointment)
    return appointment
