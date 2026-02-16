"""
ASGI config for BlinkChat. Supports HTTP and WebSocket.
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from chat.middleware import JWTWebSocketAuthMiddleware
from chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': JWTWebSocketAuthMiddleware(URLRouter(websocket_urlpatterns)),
})
