import jwt

from datetime import datetime

from config import settings
from src.auth.models import User
from src.auth.service import UserService


async def get_user(token) -> User | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
    except jwt.PyJWTError:
        return None

    if datetime.fromtimestamp(payload.get('exp')) < datetime.now():
        return None

    db_session = await UserService.ainit()
    if user := await db_session.filter(id=payload.get('user_id')):
        return user
