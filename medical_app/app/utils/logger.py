# app/utils/logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys
from pythonjsonlogger import jsonlogger
from app.config import settings

# Crear logger
logger = logging.getLogger("api-security")
logger.setLevel(logging.INFO)

# Evita duplicar handlers si se importa varias veces
if not logger.handlers:
    # Handler para consola (stream)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    # Opcional: handler para archivo rotativo
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    file_handler = RotatingFileHandler(
        logs_dir / "api.log", maxBytes=1_000_000, backupCount=5
    )
    file_formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

# Ejemplo de uso
# logger.info("API Request", extra={
#     "api_key": api_key[:6] + "***",
#     "endpoint": request.url.path,
#     "status": "success"
# })

})

def setup_logger():
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logger = logging.getLogger("dermscan")
    logger.setLevel(logging.DEBUG)

    # Formato
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]"
    )

    # Handler para archivo
    file_handler = RotatingFileHandler(
        logs_dir / "dermscan.log",
        maxBytes=1024 * 1024 * 5,  # 5MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logger()
