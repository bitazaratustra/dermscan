from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, upload
from .routes import appointments
from .routes import predictions
from .routes import user
from .routes import chat
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse



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
    # Le dice a FastAPI que, cuando haya un 422, devuelva este JSON con detalles.
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),  # lista de errores de Pydantic
            "body": exc.body         # el body que llegó en la petición
        },
    )


app.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(upload.router, prefix="/upload", tags=["predictions"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(user.router, prefix="/user", tags=["user"])

#app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
#app.include_router(video.router, prefix="/video", tags=["video"])

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción cambia esto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de rutas estáticas
static_dir = Path("app/static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Ruta principal
@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse("app/static/index.html")


# Routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])

# Health check
@app.get("/status")
async def status():
    return {"status": "ok"}
