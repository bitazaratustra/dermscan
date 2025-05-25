# app/services/video.py
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from app.config import settings
from app.utils.logger import logger

def create_video_room(room_name: str):
    # Implementar lógica de creación de sala usando Twilio API
    pass

def generate_access_token(identity: str, room_name: str):
    try:
        token = AccessToken(
            settings.twilio_account_sid,
            settings.twilio_api_key,
            settings.twilio_api_secret,
            identity=identity
        )

        video_grant = VideoGrant(room=room_name)
        token.add_grant(video_grant)

        return token.to_jwt()

    except Exception as e:
        logger.error(f"Error generating video token: {str(e)}")
        raise
