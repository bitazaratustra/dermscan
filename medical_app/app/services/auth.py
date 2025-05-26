from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from ..schemas import user as user_schemas
from ..models import user
from ..models.user import User
from ..utils.security import get_password_hash, verify_password
import uuid
import hashlib
from ..config import settings


SECRET_KEY = "super-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )

def get_user_by_email(db: Session, email: str):
    return db.query(user.User).filter(user.User.email == email).first()


def create_user(db: Session, user_data: user_schemas.UserCreate) -> user.User:
    hashed_pw = get_password_hash(user_data.password)
    db_user = user.User(
        email=user_data.email,
        hashed_password=hashed_pw,
        full_name=user_data.full_name  # Usar el campo correcto
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> User | bool:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user




def generate_secure_api_key():
    # Generar clave única con UUID
    raw_key = str(uuid.uuid4())
    # Hashear la clave para almacenamiento seguro
    hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
    return raw_key, hashed_key

# Ejemplo de uso (ejecutar una vez para generar la clave)
# api_key, hashed_api_key = generate_secure_api_key()
# print(f"Guarda esta clave en OpenAI GPT: {api_key}")
# print(f"Guarda este hash en tu .env: OPENAI_API_KEY_HASH={hashed_api_key}")
