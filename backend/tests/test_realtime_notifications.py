"""
Tests for real-time notifications system
"""
import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from api.services.notification_service import NotificationService
from api.background.redis_listener import RedisWebSocketBridge


class TestNotificationService:
    """Test NotificationService functionality"""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        redis_mock = AsyncMock()
        redis_mock.publish = AsyncMock(return_value=1)
        redis_mock.pubsub = Mock()
        redis_mock.pubsub_channels = AsyncMock(return_value=[b"match:123", b"live:all"])
        redis_mock.pubsub_numsub = AsyncMock(return_value={"match:123": 5})
        return redis_mock

    @pytest.fixture
    def notification_service(self, mock_redis):
        """Create NotificationService instance"""
        return NotificationService(mock_redis)

    @pytest.mark.asyncio
    async def test_publish_match_update(self, notification_service, mock_redis):
        """Test publishing match update"""
        match_id = "test123"
        match_data = {
            "score": {"home": 2, "away": 1},
            "minute": 67,
            "status": "live",
            "league": {"id": "premier-league"}
        }

        result = await notification_service.publish_match_update(
            match_id=match_id,
            match_data=match_data,
            update_type="score"
        )

        assert result is True
        assert mock_redis.publish.call_count == 4  # match, live, league, all channels

    @pytest.mark.asyncio
    async def test_publish_match_event(self, notification_service, mock_redis):
        """Test publishing match event"""
        match_id = "test123"
        event = {
            "type": "goal",
            "minute": 45,
            "player": "Messi",
            "team": "home"
        }
        match_data = {
            "status": "live",
            "league": {"id": "premier-league"}
        }

        result = await notification_service.publish_match_event(
            match_id=match_id,
            event=event,
            match_data=match_data
        )

        assert result is True
        assert mock_redis.publish.called

    @pytest.mark.asyncio
    async def test_publish_match_status_change(self, notification_service, mock_redis):
        """Test publishing match status change"""
        match_id = "test123"
        match_data = {
            "status": "live",
            "league": {"id": "premier-league"}
        }

        result = await notification_service.publish_match_status_change(
            match_id=match_id,
            old_status="scheduled",
            new_status="live",
            match_data=match_data
        )

        assert result is True
        assert mock_redis.publish.called

    @pytest.mark.asyncio
    async def test_get_channel_name(self, notification_service):
        """Test channel name generation"""
        # Match channel with ID
        channel = notification_service._get_channel_name("match", "123")
        assert channel == "match:123"

        # League channel
        channel = notification_service._get_channel_name("league", "premier-league")
        assert channel == "league:premier-league"

        # Live channel without ID
        channel = notification_service._get_channel_name("live")
        assert channel == "live"

    @pytest.mark.asyncio
    async def test_get_active_channels(self, notification_service, mock_redis):
        """Test getting active channels"""
        channels = await notification_service.get_active_channels()

        assert isinstance(channels, list)
        assert "match:123" in channels
        assert "live:all" in channels

    @pytest.mark.asyncio
    async def test_get_channel_subscriber_count(self, notification_service, mock_redis):
        """Test getting subscriber count"""
        count = await notification_service.get_channel_subscriber_count("match:123")

        assert count == 5
        mock_redis.pubsub_numsub.assert_called_once_with("match:123")


class TestRedisWebSocketBridge:
    """Test RedisWebSocketBridge functionality"""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        redis_mock = AsyncMock()

        # Mock pubsub
        pubsub_mock = AsyncMock()
        pubsub_mock.subscribe = AsyncMock()
        pubsub_mock.psubscribe = AsyncMock()
        pubsub_mock.unsubscribe = AsyncMock()
        pubsub_mock.punsubscribe = AsyncMock()
        pubsub_mock.close = AsyncMock()

        # Create async iterator for listen
        async def async_listen():
            # Simulate some messages
            messages = [
                {
                    "type": "subscribe",
                    "channel": "all"
                },
                {
                    "type": "message",
                    "channel": "match:123",
                    "data": json.dumps({
                        "type": "match_update",
                        "match_id": "123",
                        "data": {"score": {"home": 1, "away": 0}},
                        "timestamp": datetime.utcnow().isoformat()
                    })
                }
            ]
            for msg in messages:
                yield msg
            # Keep the iterator alive
            while True:
                await asyncio.sleep(1)

        pubsub_mock.listen = async_listen

        redis_mock.pubsub = Mock(return_value=pubsub_mock)

        return redis_mock

    @pytest.fixture
    def mock_ws_manager(self):
        """Create mock WebSocket manager"""
        ws_manager = AsyncMock()
        ws_manager.broadcast = AsyncMock()
        return ws_manager

    @pytest.fixture
    def bridge(self, mock_redis, mock_ws_manager):
        """Create RedisWebSocketBridge instance"""
        with patch('api.background.redis_listener.get_connection_manager', return_value=mock_ws_manager):
            return RedisWebSocketBridge(mock_redis)

    @pytest.mark.asyncio
    async def test_handle_message(self, bridge, mock_ws_manager):
        """Test message handling"""
        channel = "match:123"
        data = {
            "type": "match_update",
            "match_id": "123",
            "data": {"score": {"home": 1, "away": 0}},
            "timestamp": datetime.utcnow().isoformat()
        }

        await bridge.handle_message(channel, data)

        # Verify broadcast was called
        mock_ws_manager.broadcast.assert_called_once()
        call_args = mock_ws_manager.broadcast.call_args
        assert call_args[0][0] == channel
        assert call_args[0][1]["type"] == "match_update"

    @pytest.mark.asyncio
    async def test_start_stop_bridge(self, bridge):
        """Test starting and stopping bridge"""
        # This is a basic test - full testing requires running event loop
        assert bridge.is_running is False

        # Start bridge in background
        start_task = asyncio.create_task(bridge.start())

        # Give it a moment to start
        await asyncio.sleep(0.1)

        # Stop bridge
        await bridge.stop()

        # Cancel start task
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass

        assert bridge.is_running is False


class TestCeleryTaskIntegration:
    """Test Celery task integration with notifications"""

    @pytest.mark.asyncio
    async def test_serialize_match_data(self):
        """Test match data serialization"""
        from tasks.live_scores import serialize_match_data
        from bson import ObjectId

        # Create test data with ObjectId and datetime
        data = {
            "_id": ObjectId(),
            "match_date": datetime(2024, 11, 9, 14, 30),
            "score": {"home": 2, "away": 1},
            "home_team": {
                "name": "Team A",
                "id": ObjectId()
            },
            "events": [
                {
                    "type": "goal",
                    "minute": 45,
                    "timestamp": datetime(2024, 11, 9, 14, 45)
                }
            ]
        }

        serialized = serialize_match_data(data)

        # Check ObjectId is converted to string
        assert isinstance(serialized["_id"], str)

        # Check datetime is converted to ISO string
        assert isinstance(serialized["match_date"], str)
        assert "2024-11-09" in serialized["match_date"]

        # Check nested objects are serialized
        assert isinstance(serialized["home_team"]["id"], str)

        # Check list items are serialized
        assert isinstance(serialized["events"][0]["timestamp"], str)

        # Check regular values are preserved
        assert serialized["score"] == {"home": 2, "away": 1}


class TestWebSocketIntegration:
    """Integration tests for WebSocket + Redis"""

    @pytest.mark.asyncio
    async def test_end_to_end_message_flow(self):
        """Test complete message flow from Redis to WebSocket"""
        # This test requires a running Redis and WebSocket server
        # Skip in unit tests, run in integration tests
        pytest.skip("Requires running Redis and WebSocket server")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
