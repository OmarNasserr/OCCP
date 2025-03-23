from django.urls import path
from .views import ChargerListAPIView, StartChargingAPIView

urlpatterns = [
    path('', ChargerListAPIView.as_view(), name='charger-list'),
    path('start/<str:charge_point_id>/', StartChargingAPIView.as_view(), name='start-charging'),
]