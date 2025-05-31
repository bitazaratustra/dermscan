import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..config.settings import settings
from ..schemas.chat import ChatRequest
from ..models.prediction import Prediction
from app.middleware.security import OpenAIAuth
from openai import RateLimitError

# Esta es la clase cliente nueva de openai>=1.0.0
from openai import OpenAI

router = APIRouter()
security = OpenAIAuth()

# Instanciamos el cliente pasando la API key desde settings
client = OpenAI(api_key=settings.openai_api_key)

@router.post("", response_model=dict)
async def chat_with_diagnosis(chat_req: ChatRequest, token: str = Depends(security), db: Session = Depends(get_db)):
    try:
        pred = db.query(Prediction).get(chat_req.prediction_id)
        if not pred:
            raise HTTPException(status_code=404, detail="Prediction not found")

        prompt = (
            f"Diagnóstico dermatológico: {pred.diagnosis}\n"
            f"Confianza: {pred.confidence:.2%}\n\n"
            f"Paciente pregunta: {chat_req.user_message}\n"
            "Por favor, proporciona una recomendación clínica."
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un médico que da recomendaciones clínicas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200  # opcional para limitar costos
        )

        content = response.choices[0].message.content
        return {
            "diagnosis": pred.diagnosis,
            "confidence": pred.confidence,
            "recommendation": content
        }

    except RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Se superó la cuota de peticiones en OpenAI. Revisá tu plan de facturación."
        )
    except Exception as e:
        logging.exception("Error en /chat/:")
        raise HTTPException(status_code=500, detail=f"Error interno: {e}")
