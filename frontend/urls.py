from django.urls import path
from .views import dashboard, charger_detail, run_simulator, stop_simulator
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name="frontend/login.html"), name='login'),
    path('dashboard', dashboard, name='dashboard'),
    path('charger/<str:charge_point_id>/', charger_detail, name='charger_detail'),
    path("run-simulator/", run_simulator, name="run-simulator"),
    path("stop-simulator/", stop_simulator, name="stop-simulator"),
]