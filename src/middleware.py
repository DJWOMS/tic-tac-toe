from typing import Tuple

from starlette.authentication import AuthenticationBackend, AuthCredentials

from src.auth.auth import get_user
from src.auth.models import User


class JwtWebSocketsAuthMiddleware(AuthenticationBackend):

    async def authenticate(self, conn) -> Tuple[AuthCredentials, User] | None:
        if conn.scope["type"] != 'websocket':
            return

        if token := conn.query_params.get('token'):
            if user := await get_user(token):
                return AuthCredentials(["authenticated"]), user

