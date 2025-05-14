from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from app.services import file as file_service
from ml.classifier import SkinClassifier
import json
import os

router = APIRouter()


with open("ml/class_names.json") as f:
    class_names = json.load(f)

model = SkinClassifier("ml/model.pth", class_names)

@router.post("/lesion")
async def upload_lesion_image(file: UploadFile = File(...)):
    try:

        filename = await file_service.save_upload_image(file)
        image_path = os.path.join("app/static/uploads", filename)

        prediction = model.predict(image_path)

        return JSONResponse(
            content={
                "filename": filename,
                "prediction": prediction,
                "message": "Upload and classification successful"
            },
            status_code=201
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
