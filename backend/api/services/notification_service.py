"""
Notification service for real-time updates via Redis Pub/Sub
"""
from typing import Dict, Any, Optional, List
import json
import asyncio
import structlog
from redis.asyncio import Redis
from datetime import datetime

logger = structlog.get_logger()


class NotificationService:
    """
    Service for publishing and subscribing to real-time notifications
    Uses Redis Pub/Sub for distributed messaging
    """

    # Channel prefixes
    CHANNEL_MATCH = "match"
    CHANNEL_LEAGUE = "league"
    CHANNEL_LIVE = "live"
    CHANNEL_ALL = "all"

    def __init__(self, redis_client: Redis):
        """
        Initialize notification service

        Args:
            redis_client: Async Redis client instance
        """
        self.redis = redis_client

    def _get_channel_name(self, channel_type: str, identifier: Optional[str] = None) -> str:
        """
        Generate channel name

        Args:
            channel_type: Type of channel (match, league, live, all)
            identifier: Optional identifier (match_id, league_id, etc.)

        Returns:
            Full channel name
        """
        if identifier:
            return f"{channel_type}:{identifier}"
        return channel_type

    async def publish_match_update(
        self,
        match_id: str,
        match_data: Dict[str, Any],
        update_type: str = "update"
    ) -> bool:
        """
        Publish match update to Redis

        Args:
            match_id: Match ID
            match_data: Match data to publish
            update_type: Type of update (update, score, event, status)

        Returns:
            True if published successfully
        """
        try:
            message = {
                "type": f"match_{update_type}",
                "match_id": match_id,
                "data": match_data,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Publish to match-specific channel
            match_channel = self._get_channel_name(self.CHANNEL_MATCH, match_id)
            await self.redis.publish(match_channel, json.dumps(message))

            # If match is live, also publish to live channel
            if match_data.get("status") in ["live", "halftime"]:
                live_channel = self._get_channel_name(self.CHANNEL_LIVE, "all")
                await self.redis.publish(live_channel, json.dumps(message))

            # Publish to league channel if league_id exists
            league_id = match_data.get("league", {}).get("id")
            if league_id:
                league_channel = self._get_channel_name(self.CHANNEL_LEAGUE, league_id)
                await self.redis.publish(league_channel, json.dumps(message))

            # Publish to general updates channel
            all_channel = self._get_channel_name(self.CHANNEL_ALL)
            await self.redis.publish(all_channel, json.dumps(message))

            logger.info(
                "match_update_published",
                match_id=match_id,
                update_type=update_type,
                status=match_data.get("status")
            )

            return True

        except Exception as e:
            logger.error(
                "publish_match_update_failed",
                match_id=match_id,
                error=str(e)
            )
            return False

    async def publish_match_score_update(
        self,
        match_id: str,
        score: Dict[str, int],
        minute: Optional[int] = None,
        match_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish match score update

        Args:
            match_id: Match ID
            score: Score data (home, away)
            minute: Current match minute
            match_data: Full match data (optional)

        Returns:
            True if published successfully
        """
        update_data = match_data or {}
        update_data["score"] = score

        if minute is not None:
            update_data["minute"] = minute

        return await self.publish_match_update(match_id, update_data, "score")

    async def publish_match_event(
        self,
        match_id: str,
        event: Dict[str, Any],
        match_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish match event (goal, card, substitution, etc.)

        Args:
            match_id: Match ID
            event: Event data
            match_data: Full match data (optional)

        Returns:
            True if published successfully
        """
        update_data = match_data or {}
        update_data["event"] = event

        return await self.publish_match_update(match_id, update_data, "event")

    async def publish_match_status_change(
        self,
        match_id: str,
        old_status: str,
        new_status: str,
        match_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish match status change (scheduled -> live -> finished)

        Args:
            match_id: Match ID
            old_status: Previous status
            new_status: New status
            match_data: Full match data (optional)

        Returns:
            True if published successfully
        """
        update_data = match_data or {}
        update_data["old_status"] = old_status
        update_data["status"] = new_status

        logger.info(
            "match_status_changed",
            match_id=match_id,
            old_status=old_status,
            new_status=new_status
        )

        return await self.publish_match_update(match_id, update_data, "status")

    async def publish_league_table_update(
        self,
        league_id: str,
        table_data: Dict[str, Any]
    ) -> bool:
        """
        Publish league table update

        Args:
            league_id: League ID
            table_data: League table data

        Returns:
            True if published successfully
        """
        try:
            message = {
                "type": "league_table_update",
                "league_id": league_id,
                "data": table_data,
                "timestamp": datetime.utcnow().isoformat()
            }

            league_channel = self._get_channel_name(self.CHANNEL_LEAGUE, league_id)
            await self.redis.publish(league_channel, json.dumps(message))

            logger.info("league_table_update_published", league_id=league_id)

            return True

        except Exception as e:
            logger.error(
                "publish_league_table_update_failed",
                league_id=league_id,
                error=str(e)
            )
            return False

    async def subscribe_to_channels(
        self,
        channels: List[str],
        callback: callable
    ) -> None:
        """
        Subscribe to Redis channels and process messages

        Args:
            channels: List of channel names to subscribe to
            callback: Async callback function to handle messages
        """
        try:
            pubsub = self.redis.pubsub()

            # Subscribe to channels
            await pubsub.subscribe(*channels)

            logger.info("subscribed_to_channels", channels=channels)

            # Listen for messages
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        # Parse message data
                        data = json.loads(message["data"])
                        channel = message["channel"]

                        # Call the callback function
                        await callback(channel, data)

                    except json.JSONDecodeError as e:
                        logger.error(
                            "message_parse_failed",
                            channel=message["channel"],
                            error=str(e)
                        )
                    except Exception as e:
                        logger.error(
                            "callback_failed",
                            channel=message["channel"],
                            error=str(e)
                        )

        except Exception as e:
            logger.error("subscription_failed", error=str(e))
            raise
        finally:
            await pubsub.unsubscribe(*channels)
            await pubsub.close()

    async def get_active_channels(self) -> List[str]:
        """
        Get list of active pub/sub channels

        Returns:
            List of active channel names
        """
        try:
            channels = await self.redis.pubsub_channels()
            return [ch.decode() if isinstance(ch, bytes) else ch for ch in channels]
        except Exception as e:
            logger.error("get_active_channels_failed", error=str(e))
            return []

    async def get_channel_subscriber_count(self, channel: str) -> int:
        """
        Get number of subscribers for a channel

        Args:
            channel: Channel name

        Returns:
            Number of subscribers
        """
        try:
            result = await self.redis.pubsub_numsub(channel)
            return result[channel] if channel in result else 0
        except Exception as e:
            logger.error(
                "get_subscriber_count_failed",
                channel=channel,
                error=str(e)
            )
            return 0
