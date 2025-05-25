import httpx
from app.config import settings

class OpenAIClient:
    def __init__(self):
        self.base_url = "https://api.openai.com/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "OpenAI-Organization": settings.openai_org_id,
            "OpenAI-Project": settings.openai_project_id,
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages, model="gpt-4"):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            return response.json()
