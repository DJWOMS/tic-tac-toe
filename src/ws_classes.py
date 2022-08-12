from typing import List, Any

from starlette.endpoints import WebSocketEndpoint
from starlette.websockets import WebSocket


class WebSocketManager:
    def __init__(self):
        self.connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await self.add_connection(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        await self.delete_connection(websocket)

    async def add_connection(self, websocket: WebSocket) -> None:
        self.connections.append(websocket)

    async def delete_connection(self, websocket: WebSocket) -> None:
        self.connections.remove(websocket)

    async def send_message(self, websocket: WebSocket, message: dict) -> None:
        await websocket.send_json(message)

    async def broadcast(self, message: dict) -> None:
        for connection in self.connections:
            await connection.send_json(message)


class WebSocketActions(WebSocketEndpoint):
    encoding: str = 'json'
    actions: List[str] = []

    async def actions_not_allowed(self, websocket: WebSocket, data: Any) -> None:
        await websocket.send_json({'action': 'Not found'})

    async def on_receive(self, websocket: WebSocket, data: Any):
        if data['action'] in self.actions:
            handler = getattr(self, data['action'], self.actions_not_allowed)
        else:
            handler = self.actions_not_allowed
        return await handler(websocket, data)


class WebSocketBroadcast(WebSocketActions):
    manager = WebSocketManager()

    async def on_connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        await self.manager.connect(websocket)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> None:
        await self.manager.disconnect(websocket)
