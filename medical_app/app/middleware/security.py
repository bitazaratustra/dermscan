from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class OpenAIAuth(HTTPBearer):
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials.scheme != "Bearer":
            raise HTTPException(status_code=403, detail="Esquema de autenticación inválido")

        # Aquí puedes agregar validación adicional si necesitas verificar tokens propios
        return credentials.credentials
