import asyncio
import datetime
import sys
import websockets
import logging
from ocpp.v16 import ChargePoint as OCPPChargePoint
from ocpp.v16 import call

# Create a ChargePoint subclass for the simulator.
class ChargePoint(OCPPChargePoint):
    async def send_boot_notification(self):
        request = call.BootNotification(
            charge_point_model="TestPointModel",
            charge_point_vendor="TestPointVendor"
        )
        response = await self.call(request)
        print(f"BootNotification response: {response}")

    async def send_heartbeat(self):
        request = call.Heartbeat()
        response = await self.call(request)
        print(f"Heartbeat response: {response}")

    async def start_transaction(self):
        request = call.StartTransaction(
            connector_id=1,
            id_tag="TESTTAG",
            meter_start=0,
            timestamp=f"{datetime.datetime.now()}"
        )
        response = await self.call(request)
        print(f"StartTransaction response: {response}")
        return response.transaction_id

    async def stop_transaction(self, transaction_id):
        request = call.StopTransaction(
            transaction_id=transaction_id,
            meter_stop=100,
            timestamp=f"{datetime.datetime.now()}"
        )
        response = await self.call(request)
        print(f"StopTransaction response: {response}")

async def main(charger_id):
    ws_url = f"ws://localhost:8000/ws/ocpp/{charger_id}/"
    async with websockets.connect(ws_url) as ws:
        cp_instance = ChargePoint(charger_id, ws)
        # Start processing incoming messages in the background.
        asyncio.create_task(cp_instance.start())
        # Send a BootNotification to the server.
        await cp_instance.send_boot_notification()
        # Send a Heartbeat every 10 seconds.
        asyncio.create_task(send_heartbeat_periodically(cp_instance))
        # Start a transaction after 5 seconds.
        await asyncio.sleep(5)
        transaction_id = await cp_instance.start_transaction()
        # Stop the transaction after 10 seconds.
        await asyncio.sleep(10)
        await cp_instance.stop_transaction(transaction_id)
        # Keep the connection open to simulate an active charger.
        while True:
            await asyncio.sleep(10)

async def send_heartbeat_periodically(cp_instance):
    while True:
        await cp_instance.send_heartbeat()
        await asyncio.sleep(10)  # Send a heartbeat every 10 seconds

if __name__ == '__main__':
    # Enable logging to see the connection process.
    logging.basicConfig(level=logging.INFO)

    # Get charger ID from command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python simulator.py <charger_id>")
        sys.exit(1)
    charger_id = sys.argv[1]

    # Run the simulator
    asyncio.run(main(charger_id))