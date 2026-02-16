"""
JWT auth for WebSocket: read token from query string and set scope['user'].
"""
import logging
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


class JWTWebSocketAuthMiddleware:
    """
    Resolve user from JWT in query string (e.g. ?token=...) for WebSocket.
    If no token or invalid, scope['user'] remains AnonymousUser.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "websocket":
            return await self.app(scope, receive, send)

        query = parse_qs(scope.get("query_string", b"").decode())
        tokens = query.get("token") or query.get("access")
        scope["user"] = AnonymousUser()
        if tokens:
            try:
                token = AccessToken(tokens[0])
                user = await self._get_user(token)
                if user:
                    scope["user"] = user
            except Exception as e:
                logger.debug("WebSocket JWT invalid: %s", e)

        return await self.app(scope, receive, send)

    @staticmethod
    async def _get_user(token):
        from asgiref.sync import sync_to_async
        user_id = token.get("user_id")
        if not user_id:
            return None

        @sync_to_async
        def _fetch():
            try:
                return User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return None

        return await _fetch()
