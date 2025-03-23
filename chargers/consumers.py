from channels.generic.websocket import AsyncWebsocketConsumer
from ocpp.v16 import call, call_result
from ocpp.v16 import ChargePoint as BaseChargePoint
from ocpp.v16.enums import RegistrationStatus, AuthorizationStatus, ChargePointStatus
from datetime import datetime
import logging
from ocpp.routing import on
import os
import django
os.environ.setdefault('DJANDO_SETTINGS_MODULE', 'ocpp_backend.settings')
django.setup()
from .models import Charger, Transaction, StatusLog
from asgiref.sync import sync_to_async
from ocpp.v16.datatypes import IdTagInfo
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)

class ChargePoint(BaseChargePoint):
    async def send_boot_notification(self):
        request = call.BootNotification(
            charge_point_model="EVSE-123",
            charge_point_vendor="EV-Charger Inc."
        )
        response = await self.call(request)
        logger.info(f"Boot Notification Response: {response}")

    @on("BootNotification")
    async def on_boot_notification(self, charge_point_model, charge_point_vendor, **kwargs):
        logger.info(f"Received BootNotification from {charge_point_model}")
        # Create or update the charger in the database
        charger, created = await sync_to_async(Charger.objects.get_or_create)(
            charge_point_id=self.id,
            defaults={
                "charge_point_model": charge_point_model,
                "charge_point_vendor": charge_point_vendor,
            }
        )
        charger.connected_at = datetime.now().isoformat()
        await sync_to_async(charger.save)()
        # Log the status
        await sync_to_async(StatusLog.objects.create)(
            charger=charger,
            status="Connected"
        )
        # Broadcast a message to the frontend
        channel_layer = get_channel_layer()
        await channel_layer.group_send("frontend", {
            "type": "charger_update",
            "charger_id": self.id,
            "status": "Connected",
            "message": f"Charger {self.id} booted with model {charge_point_model} and vendor {charge_point_vendor}"
        })
        return call_result.BootNotification(
            current_time=datetime.now().isoformat(timespec="seconds"),
            interval=10,
            status=RegistrationStatus.accepted
        )

    @on("Heartbeat")
    async def on_heartbeat(self, **kwargs):
        logger.info("Received Heartbeat")
        # Log the heartbeat status
        charger = await sync_to_async(Charger.objects.get)(charge_point_id=self.id)
        await sync_to_async(StatusLog.objects.create)(
            charger=charger,
            status="Heartbeat"
        )
        # Broadcast heartbeat event
        channel_layer = get_channel_layer()
        await channel_layer.group_send("frontend", {
            "type": "charger_update",
            "charger_id": self.id,
            "status": "Heartbeat",
            "message": f"Heartbeat from charger {self.id} at {datetime.now().strftime('%H:%M:%S')}"
        })
        return call_result.Heartbeat(
            current_time=datetime.now().isoformat(timespec="seconds")
        )

    @on("StartTransaction")
    async def on_start_transaction(self, id_tag, connector_id, meter_start, **kwargs):
        logger.info(f"Charging started: Connector {connector_id} - ID {id_tag}")
        # Create a new transaction
        charger = await sync_to_async(Charger.objects.get)(charge_point_id=self.id)
        transaction = await sync_to_async(Transaction.objects.create)(
            charger=charger,
            id_tag=id_tag,
            connector_id=connector_id,
            meter_start=meter_start
        )
        # Log the status
        await sync_to_async(StatusLog.objects.create)(
            charger=charger,
            status="Transaction Started"
        )
        # Broadcast start transaction event
        channel_layer = get_channel_layer()
        await channel_layer.group_send("frontend", {
            "type": "charger_update",
            "charger_id": self.id,
            "status": "Transaction Started",
            "message": f"Transaction started on charger {self.id} (Transaction ID: {transaction.id})"
        })
        return call_result.StartTransaction(
            transaction_id=transaction.id,
            id_tag_info=IdTagInfo(AuthorizationStatus.accepted)
        )

    @on("StopTransaction")
    async def on_stop_transaction(self, transaction_id, meter_stop, **kwargs):
        logger.info(f"Charging stopped for transaction: {transaction_id}")
        # Update the transaction
        transaction = await sync_to_async(Transaction.objects.get)(id=transaction_id)
        transaction.meter_stop = meter_stop
        transaction.stop_time = datetime.now()
        await sync_to_async(transaction.save)()

        charger = await sync_to_async(lambda: transaction.charger)()
        # Log the status
        await sync_to_async(StatusLog.objects.create)(
            charger=charger,
            status="Transaction Stopped"
        )
        # Broadcast stop transaction event
        channel_layer = get_channel_layer()
        await channel_layer.group_send("frontend", {
            "type": "charger_update",
            "charger_id": self.id,
            "status": "Transaction Stopped",
            "message": f"Transaction {transaction_id} stopped on charger {self.id}"
        })
        return call_result.StopTransaction()

class OCPPConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.charge_point = None
        self.charge_point_id = None

    async def connect(self):
        self.charge_point_id = self.scope['url_route']['kwargs']['charge_point_id']
        self.charge_point = ChargePoint(self.charge_point_id, self)
        logger.info(f"Attempting to connect charger: {self.charge_point_id}")
        try:
            await self.accept()
            logger.info(f"Charger {self.charge_point_id} connected.")
            # Send a message to frontend group
            channel_layer = get_channel_layer()
            message = {
                "type": "charger_update",
                "charger_id": self.charge_point_id,
                "status": "Connected",
                "message": f"Charger {self.charge_point_id} connected."
            }
            logger.info(f"Sending WebSocket message: {message}")
            await channel_layer.group_send("frontend", message)
        except Exception as e:
            logger.error(f"Failed to connect charger {self.charge_point_id}: {e}")
            raise
    async def disconnect(self, close_code):
        logger.info(f"Charger {self.charge_point_id} disconnected.")
        # Update the charger status in the database
        try:
            charger = await sync_to_async(Charger.objects.get)(charge_point_id=self.charge_point_id)
            charger.status = "Disconnected"
            await sync_to_async(charger.save)()
            # Log the disconnection status
            await sync_to_async(StatusLog.objects.create)(
                charger=charger,
                status="Disconnected"
            )
            # Inform frontend about disconnection
            channel_layer = get_channel_layer()
            await channel_layer.group_send("frontend", {
                "type": "charger_update",
                "charger_id": self.charge_point_id,
                "status": "Disconnected",
                "message": f"Charger {self.charge_point_id} disconnected."
            })
        except Charger.DoesNotExist:
            logger.error(f"Charger {self.charge_point_id} not found in the database.")

    async def receive(self, text_data):
        await self.charge_point.route_message(text_data)