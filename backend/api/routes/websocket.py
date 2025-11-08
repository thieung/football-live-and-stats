"""
WebSocket routes for real-time updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import structlog

logger = structlog.get_logger()
router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections and subscriptions
    """

    def __init__(self):
        # {channel: {websocket1, websocket2, ...}}
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection"""
        await websocket.accept()
        logger.info("websocket_connected")

    def disconnect(self, websocket: WebSocket):
        """Remove websocket from all channels"""
        for channel in list(self.active_connections.keys()):
            self.active_connections[channel].discard(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        logger.info("websocket_disconnected")

    def subscribe(self, channel: str, websocket: WebSocket):
        """Subscribe websocket to a channel"""
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)
        logger.info("websocket_subscribed", channel=channel)

    def unsubscribe(self, channel: str, websocket: WebSocket):
        """Unsubscribe websocket from a channel"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        logger.info("websocket_unsubscribed", channel=channel)

    async def broadcast(self, channel: str, message: dict):
        """
        Broadcast message to all subscribers of a channel
        """
        if channel not in self.active_connections:
            return

        dead_connections = set()

        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("websocket_send_failed", error=str(e))
                dead_connections.add(connection)

        # Clean up dead connections
        for conn in dead_connections:
            self.active_connections[channel].discard(conn)

        if not self.active_connections[channel]:
            del self.active_connections[channel]


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates

    Client messages:
    {
        "action": "subscribe",
        "channels": ["match:12345", "league:uuid", "live:all"]
    }

    {
        "action": "unsubscribe",
        "channels": ["match:12345"]
    }

    Server messages:
    {
        "type": "match_update",
        "channel": "match:12345",
        "data": { ... }
    }
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            action = data.get("action")
            channels = data.get("channels", [])

            if action == "subscribe":
                for channel in channels:
                    manager.subscribe(channel, websocket)

                await websocket.send_json({
                    "type": "subscribed",
                    "channels": channels
                })

            elif action == "unsubscribe":
                for channel in channels:
                    manager.unsubscribe(channel, websocket)

                await websocket.send_json({
                    "type": "unsubscribed",
                    "channels": channels
                })

            elif action == "ping":
                await websocket.send_json({
                    "type": "pong"
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error("websocket_error", error=str(e))
        manager.disconnect(websocket)


# Export manager for use in other modules
def get_connection_manager():
    """Get the global connection manager instance"""
    return manager
