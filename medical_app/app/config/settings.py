from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Solo necesitamos la API Key para cuentas personales
    openai_api_key: str

    # PostgreSQL
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "dermscan"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Database
    database_url: str

    # Email (configuración para testing)
    email_host: str = "smtp.yopmail.com"
    email_port: int = 587
    email_user: str = "tudermo@yopmail.com"  # Crea uno en yopmail.com
    email_pass: str = "password_test"
    email_sender: str = "notificaciones@dermscan.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignora variables extras no definidas

settings = Settings()
