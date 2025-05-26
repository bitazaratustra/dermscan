import logging
import openai
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..config.settings import settings
from ..schemas.chat import ChatRequest
from ..models.prediction import Prediction
from app.middleware.security import OpenAIAuth
from openai import OpenAI

router = APIRouter()
security = OpenAIAuth()
client = OpenAI()

openai.api_key = settings.openai_api_key

@router.post("/")
async def chat_with_diagnosis(
    chat_req: ChatRequest,
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    try:
        pred = db.query(Prediction).filter(Prediction.id == chat_req.prediction_id).first()
        if not pred:
            raise HTTPException(status_code=404, detail="Prediction not found")

        prompt = (
            f"Diagnóstico dermatológico: {pred.diagnosis}\n"
            f"Confianza en el diagnóstico: {pred.confidence:.2%}\n\n"
            f"Paciente pregunta: {chat_req.user_message}\n"
            "Por favor, proporciona una recomendación clínica detallada y sugerencias para el paciente."
        )

        response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente..."},
            {"role": "user", "content": prompt}
        ]
    )
        content = response.choices[0].message.content
        usage = response.usage

        return {
            "diagnosis": pred.diagnosis,
            "confidence": pred.confidence,
            "recommendation": content,
            "usage": usage,
        }

    except Exception as e:
        logging.exception("Error en /chat/:")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
