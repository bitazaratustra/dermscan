import os
from fastapi import UploadFile, HTTPException
from uuid import uuid4
from pathlib import Path

UPLOAD_DIR = Path("app/static/uploads")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

async def save_upload_image(file: UploadFile) -> str:
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = f"{uuid4().hex}{ext}"
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)

    return filename
