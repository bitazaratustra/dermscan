# app/services/chat.py
import os
import httpx
from app.config import settings
from httpx import HTTPStatusError
from app.utils.logger import logger

async def get_medical_info(diagnosis: str) -> str:
    try:
        prompt = f"""Como dermatólogo experto, proporcione:
        1. Descripción clínica de {diagnosis}
        2. Síntomas comunes
        3. Opciones de tratamiento
        4. Recomendaciones para el paciente
        En español, máximo 200 palabras, formato claro."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": "gpt-4",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
            )
    except HTTPStatusError as e:
        logger.error(f"OpenAI API Error: {e.response.status_code} - {e.response.text}")
        return "Información temporalmente no disponible"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return "Error al obtener información médica"
    return response.json()['choices'][0]['message']['content']
