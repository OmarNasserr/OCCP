from django.urls import path
from .consumers import FrontendConsumer

websocket_urlpatterns = [
    path('ws/frontend/', FrontendConsumer.as_asgi()),
]
