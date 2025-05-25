# app/routes/health.py
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return JSONResponse(
            content={"status": "OK"},
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={"status": "ERROR", "detail": str(e)},
            status_code=503
        )
