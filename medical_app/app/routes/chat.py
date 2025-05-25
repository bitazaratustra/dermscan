from fastapi import APIRouter, Depends, HTTPException
import httpx
from app.middleware.security import OpenAIAuth
from app.services.openai_client import OpenAIClient

router = APIRouter()
security = OpenAIAuth()
openai_client = OpenAIClient()

@router.post("/chat")
async def chat_endpoint(
    prompt: str,
    token: str = Depends(security)
):
    try:
        messages = [{"role": "user", "content": prompt}]
        response = await openai_client.chat_completion(messages)
        return {
            "response": response['choices'][0]['message']['content'],
            "usage": response['usage']
        }
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error en la API de OpenAI: {e.response.text}"
        )
