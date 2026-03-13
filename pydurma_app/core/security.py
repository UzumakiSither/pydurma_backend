from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from pydurma_app.config import get_settings

SECRET_KEY = get_settings().secret_key
ALGORITHM = get_settings().algorithm
TOKEN_EXPIRE_HOURS = get_settings().token_expire_hours

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int):

    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)