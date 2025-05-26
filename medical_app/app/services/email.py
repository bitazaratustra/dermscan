# app/services/email.py
from fastapi import BackgroundTasks
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.config import settings
from app.utils.logger import logger

async def send_email(
    to: str,
    subject: str,
    html_content: str,
    background_tasks: BackgroundTasks = None
):
    logger.info(f"Simulando envío de email a {to}")
    logger.info(f"Asunto: {subject}")
    logger.info(f"Contenido: {html_content}")
