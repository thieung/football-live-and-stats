"""
Background task for listening to Redis Pub/Sub and broadcasting to WebSocket clients
"""
import asyncio
import structlog
from typing import Dict, Any
from redis.asyncio import Redis

from api.core.database import get_redis
from api.services.notification_service import NotificationService
from api.routes.websocket import get_connection_manager

logger = structlog.get_logger()


class RedisWebSocketBridge:
    """
    Bridge between Redis Pub/Sub and WebSocket connections
    Listens to Redis channels and broadcasts messages to WebSocket clients
    """

    def __init__(self, redis_client: Redis):
        """
        Initialize the bridge

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
        self.notification_service = NotificationService(redis_client)
        self.ws_manager = get_connection_manager()
        self.is_running = False
        self.tasks = []

    async def handle_message(self, channel: str, data: Dict[str, Any]):
        """
        Handle incoming Redis message and broadcast to WebSocket clients

        Args:
            channel: Redis channel name
            data: Message data
        """
        try:
            logger.debug(
                "redis_message_received",
                channel=channel,
                message_type=data.get("type")
            )

            # Prepare WebSocket message
            ws_message = {
                "type": data.get("type"),
                "channel": channel,
                "data": data.get("data"),
                "timestamp": data.get("timestamp")
            }

            # Broadcast to WebSocket subscribers
            await self.ws_manager.broadcast(channel, ws_message)

            logger.debug(
                "message_broadcasted",
                channel=channel,
                type=data.get("type")
            )

        except Exception as e:
            logger.error(
                "handle_message_failed",
                channel=channel,
                error=str(e)
            )

    async def start_listening(self):
        """
        Start listening to Redis channels
        """
        if self.is_running:
            logger.warning("redis_listener_already_running")
            return

        self.is_running = True
        logger.info("redis_listener_starting")

        # Define channels to subscribe to
        channels = [
            "all",  # All updates
            "live:all",  # All live matches
            "match:*",  # All match-specific channels
            "league:*",  # All league-specific channels
        ]

        try:
            # Create subscription tasks for different channel patterns
            # Since Redis doesn't support pattern subscriptions in pubsub(),
            # we'll subscribe to specific channels and dynamic channels as needed

            # Subscribe to static channels
            static_channels = ["all", "live:all"]

            await self.notification_service.subscribe_to_channels(
                static_channels,
                self.handle_message
            )

        except Exception as e:
            logger.error("redis_listener_failed", error=str(e))
            self.is_running = False
            raise

    async def start_pattern_listening(self):
        """
        Start listening to Redis channels with pattern matching
        """
        try:
            pubsub = self.redis.pubsub()

            # Subscribe to patterns
            await pubsub.psubscribe("match:*", "league:*")

            logger.info("redis_pattern_listener_started")

            # Listen for messages
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    try:
                        import json
                        data = json.loads(message["data"])
                        channel = message["channel"]

                        await self.handle_message(channel, data)

                    except Exception as e:
                        logger.error(
                            "pattern_message_failed",
                            channel=message.get("channel"),
                            error=str(e)
                        )

        except Exception as e:
            logger.error("pattern_listener_failed", error=str(e))
            raise
        finally:
            await pubsub.punsubscribe("match:*", "league:*")
            await pubsub.close()

    async def start(self):
        """
        Start the Redis-WebSocket bridge with multiple listeners
        """
        logger.info("redis_websocket_bridge_starting")

        # Start both static and pattern listeners concurrently
        self.tasks = [
            asyncio.create_task(self.start_listening()),
            asyncio.create_task(self.start_pattern_listening()),
        ]

        logger.info("redis_websocket_bridge_started")

    async def stop(self):
        """
        Stop the Redis-WebSocket bridge
        """
        logger.info("redis_websocket_bridge_stopping")

        self.is_running = False

        # Cancel all running tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)

        self.tasks = []

        logger.info("redis_websocket_bridge_stopped")


# Global bridge instance
_bridge: RedisWebSocketBridge = None


async def start_redis_listener():
    """
    Start the Redis listener as a background task
    """
    global _bridge

    redis_client = get_redis()

    if not redis_client:
        logger.error("redis_client_not_available")
        return

    _bridge = RedisWebSocketBridge(redis_client)

    try:
        await _bridge.start()
    except Exception as e:
        logger.error("redis_listener_startup_failed", error=str(e))
        raise


async def stop_redis_listener():
    """
    Stop the Redis listener
    """
    global _bridge

    if _bridge:
        await _bridge.stop()
        _bridge = None


def get_redis_bridge():
    """
    Get the global Redis-WebSocket bridge instance
    """
    return _bridge
