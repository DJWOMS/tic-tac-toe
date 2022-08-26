import jwt
from datetime import datetime, timedelta

from config import settings


def create_token(user_id: int) -> dict:
    token = create_access_token(
        data={"user_id": user_id}, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES)
    )
    return {"access_token": token, "token_type": "Bearer"}


def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "sub": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
