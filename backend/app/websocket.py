import json
import asyncio
from fastapi import WebSocket


class WebSocketManager:

    def __init__(self):
        self.connections: list[WebSocket] = []
        self.loop = None

    def set_loop(self, loop):
        self.loop = loop
        
    def broadcast_threadsafe(
        self,
        message: dict,
    ):
        if self.loop is None:
            return

        asyncio.run_coroutine_threadsafe(
            self.broadcast(message),
            self.loop,
        )

    async def connect(
        self,
        websocket: WebSocket,
    ):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(
        self,
        websocket: WebSocket,
    ):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(
        self,
        message: dict,
    ):
        dead_connections = []

        for websocket in self.connections:
            try:
                print("Broadcast:", message)
                await websocket.send_text(
                    json.dumps(message)
                )
            except Exception:
                dead_connections.append(websocket)

        for websocket in dead_connections:
            self.disconnect(websocket)


websocket_manager = WebSocketManager()