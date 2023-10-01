"""
ASGI config for coolinary project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coolinary.settings")
django_asgi_app = get_asgi_application()
from chat.consumers import RoomConsumer as Chat
from pole_chudes.consumers import GameConsumer as PoleChudes

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter([
                path('ws/chat/', Chat.as_asgi()),
                path('ws/pole_chudes/', PoleChudes.as_asgi()),
            ]))
        ),
    }
)
