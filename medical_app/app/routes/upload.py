from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.prediction import Prediction
from ..schemas.prediction import PredictionCreate, PredictionResponse
from ..utils.security import get_current_user
from app.models.user import User
from ml.classifier import SkinClassifier
import json
import os
import uuid
from pathlib import Path

router = APIRouter(tags=["Predictions"])

# Cargar modelo
with open("ml/class_names.json") as f:
    CLASS_NAMES = json.load(f)
model = SkinClassifier("ml/model.pth", CLASS_NAMES)

async def save_upload_file(file: UploadFile) -> str:
    upload_dir = Path("app/static/uploads")
    upload_dir.mkdir(exist_ok=True)

    # Generar nombre único y seguro
    file_ext = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4()}{file_ext}"
    file_path = upload_dir / unique_name

    async with aiofiles.open(file_path, "wb") as buffer:
        await buffer.write(await file.read())

    return str(file_path.relative_to("app/static"))


@router.post("/predict", response_model=PredictionResponse)
async def predict_lesion(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # 1. Guardar imagen
        filename = await save_upload_file(file)

        # 2. Realizar predicción
        prediction = model.predict(filename)

        # 3. Guardar en base de datos
        db_prediction = Prediction(
            user_id=current_user.id,
            image_path=filename,
            diagnosis=prediction["class_name"],
            confidence=prediction["confidence"]
        )

        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)

        return db_prediction

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )
