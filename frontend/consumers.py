import json
from channels.generic.websocket import AsyncWebsocketConsumer

class FrontendConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # Join the "frontend" group to receive charger messages.
        await self.channel_layer.group_add("frontend", self.channel_name)

    async def disconnect(self, close_code):
        # Leave the "frontend" group.
        await self.channel_layer.group_discard("frontend", self.channel_name)

    # This handler is invoked when group messages are sent.
    async def charger_update(self, event):
        payload = {
            "message": event.get("message", ""),
            "charger_id": event.get("charger_id", ""),
            "status": event.get("status", "")
        }
        await self.send(text_data=json.dumps(payload))
