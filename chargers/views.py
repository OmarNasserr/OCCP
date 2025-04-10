import http

from rest_framework import generics
from .models import Charger, Transaction, StatusLog
from .serializers import ChargerSerializer
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class ChargerListAPIView(generics.ListAPIView):
    queryset = Charger.objects.all()
    serializer_class = ChargerSerializer
    permission_classes = [IsAuthenticated]


class StartChargingAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        charge_point_id = kwargs.get('charge_point_id')
        try:
            charger = Charger.objects.get(charge_point_id=charge_point_id)
            # Simulate starting a transaction
            transaction = Transaction.objects.create(
                charger=charger,
                id_tag="TESTTAG",
                connector_id=1,
                meter_start=0
            )
            # Log the status
            StatusLog.objects.create(
                charger=charger,
                status="Charging Started"
            )
            # Broadcast the charging started event
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)("frontend", {
                "type": "charger_update",
                "charger_id": charger.charge_point_id,
                "status": "Charging Started",
                "message": f"Charger {charger.charge_point_id} started charging."
            })
            return Response({
                "message": f"Charger {charger.charge_point_id} started charging.",
                "transaction_id": transaction.id,
                "status": 200
            }, status=200)
        except Charger.DoesNotExist:
            return Response({
                "message": "Charger was not found.",
                "status": 404
            }, status=404)
