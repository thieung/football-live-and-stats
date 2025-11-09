"""
Celery tasks for live score crawling
"""
from celery import shared_task
from datetime import datetime
import structlog
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

from crawlers.flashscore import FlashScoreCrawler
from crawlers.validators import transform_for_database
from api.services.match_service import MatchService

logger = structlog.get_logger()


def get_mongo_db():
    """Get MongoDB database connection"""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://admin:password123@mongodb:27017')
    mongo_db_name = os.getenv('MONGO_DB_NAME', 'football_live')
    client = AsyncIOMotorClient(mongo_uri)
    return client[mongo_db_name]


@shared_task(bind=True, max_retries=3)
def crawl_live_scores(self):
    """
    Crawl live scores from all sources
    Runs every 30 seconds
    """
    try:
        logger.info("crawl_live_scores_started")

        # Run async crawler
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(_crawl_live_scores_async())

        logger.info(
            "crawl_live_scores_completed",
            matches_updated=result.get('matches_updated', 0)
        )

        return result

    except Exception as e:
        logger.error("crawl_live_scores_failed", error=str(e))
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


async def _crawl_live_scores_async():
    """
    Async implementation of live score crawling with validation and duplicate detection
    """
    db = get_mongo_db()
    service = MatchService(db)

    # Get matches that need updates (live + today's scheduled matches)
    matches_to_update = await service.get_matches_requiring_updates(limit=100)

    logger.info(
        "matches_to_update_found",
        count=len(matches_to_update),
        live_count=sum(1 for m in matches_to_update if m.get('status') == 'live')
    )

    if not matches_to_update:
        return {
            "matches_updated": 0,
            "matches_created": 0,
            "validation_failures": 0
        }

    # Initialize crawler
    crawler = FlashScoreCrawler()

    matches_updated = 0
    matches_created = 0
    validation_failures = 0

    # Crawl each match
    for match in matches_to_update:
        try:
            external_id = match.get('external_id')
            if not external_id:
                logger.warning("match_missing_external_id", match_id=str(match.get('_id')))
                continue

            # Crawl match data
            raw_match_data = await crawler.crawl_match(external_id)

            if not raw_match_data:
                logger.debug("no_data_from_crawler", external_id=external_id)
                continue

            # Validate and transform data
            validated_data = transform_for_database(raw_match_data, match)

            if not validated_data:
                validation_failures += 1
                logger.error(
                    "data_validation_failed",
                    external_id=external_id,
                    raw_data=raw_match_data
                )
                continue

            # Upsert match with validated data
            updated_match, is_new = await service.upsert_match(
                external_id,
                validated_data
            )

            if is_new:
                matches_created += 1
            else:
                matches_updated += 1

            # Publish update via Redis (for WebSocket)
            await publish_match_update(str(updated_match['_id']), validated_data)

            logger.info(
                "match_crawl_success",
                match_id=str(updated_match['_id']),
                external_id=external_id,
                status=validated_data.get('status'),
                is_new=is_new
            )

        except Exception as e:
            logger.error(
                "match_crawl_failed",
                match_id=str(match.get('_id')),
                external_id=match.get('external_id'),
                error=str(e),
                error_type=type(e).__name__
            )
            continue

    result = {
        "matches_updated": matches_updated,
        "matches_created": matches_created,
        "validation_failures": validation_failures,
        "total_processed": matches_updated + matches_created + validation_failures
    }

    logger.info("crawl_live_scores_summary", **result)

    return result


@shared_task(bind=True, max_retries=3)
def crawl_match_events(self):
    """
    Crawl match events (goals, cards) for live matches
    Runs every 10 seconds for high-priority updates
    """
    try:
        logger.info("crawl_match_events_started")

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(_crawl_match_events_async())

        logger.info(
            "crawl_match_events_completed",
            events_found=result.get('events_found', 0)
        )

        return result

    except Exception as e:
        logger.error("crawl_match_events_failed", error=str(e))
        raise self.retry(exc=e, countdown=2 ** self.request.retries)


async def _crawl_match_events_async():
    """
    Async implementation of match events crawling with validation
    """
    db = get_mongo_db()
    service = MatchService(db)

    # Get current live matches
    live_matches = await service.get_live_matches(limit=100)

    logger.info("live_matches_for_events", count=len(live_matches))

    if not live_matches:
        return {
            "events_found": 0,
            "matches_processed": 0
        }

    crawler = FlashScoreCrawler()
    events_found = 0
    matches_processed = 0
    validation_errors = 0

    for match in live_matches:
        try:
            external_id = match.get('external_id')
            if not external_id:
                logger.warning("match_missing_external_id", match_id=str(match.get('_id')))
                continue

            matches_processed += 1

            # Crawl events
            raw_events = await crawler.crawl_match_events(external_id)

            if not raw_events:
                continue

            # Validate events using the validator
            from crawlers.validators import CrawledEvent

            validated_events = []
            for event in raw_events:
                try:
                    validated = CrawledEvent(**event)
                    validated_events.append(validated.dict(exclude_none=True))
                except Exception as e:
                    validation_errors += 1
                    logger.error(
                        "event_validation_failed",
                        match_id=str(match['_id']),
                        event=event,
                        error=str(e)
                    )

            # Check for new events by comparing with existing
            existing_events = match.get('events', [])
            existing_event_signatures = {
                f"{e['type']}_{e['minute']}_{e['player']}_{e['team']}"
                for e in existing_events
            }

            for event in validated_events:
                event_signature = f"{event['type']}_{event['minute']}_{event['player']}_{event['team']}"

                if event_signature not in existing_event_signatures:
                    # New event found!
                    await service.add_match_event(str(match['_id']), event)
                    events_found += 1

                    # Publish event notification with match data
                    await publish_match_event(str(match['_id']), event, match)

                    logger.info(
                        "new_match_event",
                        match_id=str(match['_id']),
                        event_type=event['type'],
                        minute=event['minute'],
                        player=event['player']
                    )

        except Exception as e:
            logger.error(
                "events_crawl_failed",
                match_id=str(match.get('_id')),
                external_id=match.get('external_id'),
                error=str(e),
                error_type=type(e).__name__
            )
            continue

    result = {
        "events_found": events_found,
        "matches_processed": matches_processed,
        "validation_errors": validation_errors
    }

    logger.info("crawl_match_events_summary", **result)

    return result


async def publish_match_update(match_id: str, data: dict):
    """
    Publish match update to Redis for WebSocket broadcasting
    Uses NotificationService for consistent messaging
    """
    try:
        import redis.asyncio as redis
        from api.services.notification_service import NotificationService

        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        redis_client = await redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True
        )

        notification_service = NotificationService(redis_client)

        # Serialize the match data for Redis
        serializable_data = serialize_match_data(data)

        # Publish using NotificationService
        await notification_service.publish_match_update(
            match_id=match_id,
            match_data=serializable_data,
            update_type="update"
        )

        await redis_client.close()

    except Exception as e:
        logger.error("publish_match_update_failed", match_id=match_id, error=str(e))


async def publish_match_event(match_id: str, event: dict, match_data: dict = None):
    """
    Publish match event (goal, card) to Redis
    Uses NotificationService for consistent messaging
    """
    try:
        import redis.asyncio as redis
        from api.services.notification_service import NotificationService

        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        redis_client = await redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=True
        )

        notification_service = NotificationService(redis_client)

        # Serialize the data
        serializable_match_data = serialize_match_data(match_data) if match_data else {}

        # Publish using NotificationService
        await notification_service.publish_match_event(
            match_id=match_id,
            event=event,
            match_data=serializable_match_data
        )

        await redis_client.close()

    except Exception as e:
        logger.error("publish_match_event_failed", match_id=match_id, error=str(e))


def serialize_match_data(data: dict) -> dict:
    """
    Serialize match data for Redis/JSON transmission
    Converts ObjectId and datetime objects to strings
    """
    if not data:
        return {}

    serialized = {}

    for key, value in data.items():
        if key == '_id':
            # Convert ObjectId to string
            serialized[key] = str(value)
        elif isinstance(value, datetime):
            # Convert datetime to ISO format string
            serialized[key] = value.isoformat()
        elif isinstance(value, dict):
            # Recursively serialize nested dicts
            serialized[key] = serialize_match_data(value)
        elif isinstance(value, list):
            # Serialize list items
            serialized[key] = [
                serialize_match_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            serialized[key] = value

    return serialized
