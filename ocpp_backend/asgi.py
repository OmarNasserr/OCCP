"""
ASGI config for ocpp_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import chargers.routing
import frontend.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ocpp_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        chargers.routing.websocket_urlpatterns + frontend.routing.websocket_urlpatterns
    ),
})