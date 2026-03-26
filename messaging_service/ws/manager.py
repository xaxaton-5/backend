from typing import Dict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[websocket.account_id] = websocket

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket.account_id, 0)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


def get_connection_manager():
    if not hasattr(get_connection_manager, 'manager'):
        get_connection_manager.manager = ConnectionManager()
    return get_connection_manager.manager
