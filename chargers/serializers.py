from rest_framework import serializers
from .models import Charger, Transaction, StatusLog

class ChargerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Charger
        fields = ['charge_point_id', 'charge_point_model', 'charge_point_vendor', 'status', 'connected_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'charger', 'id_tag', 'connector_id', 'meter_start', 'meter_stop', 'start_time', 'stop_time']

class StatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusLog
        fields = ['id', 'charger', 'status', 'timestamp']