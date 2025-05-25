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
    message = Mail(
        from_email=settings.email_sender,
        to_emails=to,
        subject=subject,
        html_content=html_content
    )

    try:
        sg = SendGridAPIClient(settings.sendgrid_api_key)

        if background_tasks:
            background_tasks.add_task(sg.send, message)
        else:
            sg.send(message)

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise
