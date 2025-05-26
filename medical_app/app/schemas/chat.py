# app/schemas/chat.py
from pydantic import BaseModel

class ChatRequest(BaseModel):
    prediction_id: int
    user_message: str
