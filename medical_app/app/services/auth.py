from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from medical_app.app.schemas import user
from medical_app.app.models import user
from ..models.user import User
from app.utils.security import get_password_hash, verify_password
import uuid
import hashlib
from app.config import settings

SECRET_KEY = "super-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_email(db: Session, email: str):
    return db.query(user.User).filter(user.User.email == email).first()


def create_user(db: Session, user: user.UserCreate):
    hashed_pw = get_password_hash(user.password)
    db_user = user.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
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
api_key, hashed_api_key = generate_secure_api_key()
print(f"Guarda esta clave en OpenAI GPT: {api_key}")
print(f"Guarda este hash en tu .env: OPENAI_API_KEY_HASH={hashed_api_key}")
