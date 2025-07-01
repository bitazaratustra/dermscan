from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError


from app.routes import auth, upload, appointments, predictions, user, chat, doctors

app = FastAPI(
    title="DermScan API",
    description="API para diagnóstico dermatológico integrado",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body
        },
    )


BASE_DIR = Path(__file__).resolve().parent
static_dir = BASE_DIR / "static"
uploads_dir = BASE_DIR / "static" / "uploads"


uploads_dir.mkdir(parents=True, exist_ok=True)

app.mount("/static/uploads", StaticFiles(directory=str(uploads_dir)), name="uploaded_images")
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(upload.router, prefix="/upload", tags=["predictions"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(user.router, prefix="/user", tags=["user"])
app.include_router(doctors.router, prefix="/doctor")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("app/static/index.html")

@app.get("/status")
async def status():
    return {"status": "ok"}
