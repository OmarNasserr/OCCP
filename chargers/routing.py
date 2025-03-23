from django.urls import path
from .consumers import OCPPConsumer

websocket_urlpatterns = [
    path('ws/ocpp/<str:charge_point_id>/', OCPPConsumer.as_asgi()),
]