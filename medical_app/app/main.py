from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routes import auth, upload

app = FastAPI(title="DermScan - MVP")

# Montar archivos estáticos (imágenes subidas)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Cargar templates
templates = Jinja2Templates(directory="app/templates")

# Rutas principales
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(upload.router, prefix="/upload", tags=["upload"])

@app.get("/")
def root():
    return {"message": "DermaScan API is running"}

# Ruta para formulario web simple
@app.get("/form")
def form_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})
