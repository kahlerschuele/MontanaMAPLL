"""
AISStream WebSocket bridge for Montana map
Connects to AISStream API and provides vessel data via WebSocket
"""

import asyncio
import json
import websockets
from typing import Set
from fastapi import WebSocket

AIS_API_KEY = "c40e449801077ff2bdc0e0f556c5272c188a4dcd"
AIS_STREAM_URL = "wss://stream.aisstream.io/v0/stream"

# Montana bounding box (approximately)
# Montana spans roughly 104°W to 116°W, 45°N to 49°N
MONTANA_BBOX = [
    [-116.0, 44.0],  # SW corner
    [-104.0, 49.5]   # NE corner
]

class AISStreamManager:
    def __init__(self):
        self.clients: Set[WebSocket] = set()
        self.ais_connection = None
        self.running = False

    async def connect_to_ais_stream(self):
        """Connect to AISStream and subscribe to Montana area"""
        try:
            async with websockets.connect(AIS_STREAM_URL) as websocket:
                self.ais_connection = websocket

                # Subscribe to Montana bounding box
                subscription_message = {
                    "APIKey": AIS_API_KEY,
                    "BoundingBoxes": [MONTANA_BBOX]
                }

                await websocket.send(json.dumps(subscription_message))
                print("OK - Connected to AISStream")

                # Listen for messages
                async for message in websocket:
                    if self.clients:
                        data = json.loads(message)
                        # Broadcast to all connected clients
                        await self.broadcast(data)

        except Exception as e:
            print(f"AISStream connection error: {e}")
            await asyncio.sleep(5)  # Wait before reconnecting

    async def broadcast(self, message: dict):
        """Broadcast AIS message to all connected WebSocket clients"""
        if not self.clients:
            return

        # Format message for map display
        formatted_message = json.dumps(message)

        disconnected_clients = set()
        for client in self.clients:
            try:
                await client.send_text(formatted_message)
            except Exception:
                disconnected_clients.add(client)

        # Remove disconnected clients
        self.clients -= disconnected_clients

    async def add_client(self, websocket: WebSocket):
        """Add a new WebSocket client"""
        await websocket.accept()
        self.clients.add(websocket)
        print(f"AIS client connected. Total clients: {len(self.clients)}")

    async def remove_client(self, websocket: WebSocket):
        """Remove a WebSocket client"""
        self.clients.discard(websocket)
        print(f"AIS client disconnected. Total clients: {len(self.clients)}")

    async def start(self):
        """Start the AIS stream manager"""
        self.running = True
        while self.running:
            try:
                await self.connect_to_ais_stream()
            except Exception as e:
                print(f"AIS stream error: {e}")
                await asyncio.sleep(5)

# Global manager instance
ais_manager = AISStreamManager()
