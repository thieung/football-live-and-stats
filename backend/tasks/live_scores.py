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
    Async implementation of live score crawling
    """
    db = get_mongo_db()
    service = MatchService(db)

    # Get current live matches from database
    live_matches = await service.get_live_matches(limit=100)

    logger.info("live_matches_found", count=len(live_matches))

    if not live_matches:
        return {"matches_updated": 0}

    # Initialize crawler
    crawler = FlashScoreCrawler()

    matches_updated = 0

    # Crawl each live match
    for match in live_matches:
        try:
            external_id = match.get('external_id')
            if not external_id:
                continue

            # Crawl match data
            match_data = await crawler.crawl_match(external_id)

            if match_data:
                # Update match in database
                updated = await service.update_match(
                    str(match['_id']),
                    match_data
                )

                if updated:
                    matches_updated += 1

                    # Publish update via Redis (for WebSocket)
                    await publish_match_update(str(match['_id']), match_data)

        except Exception as e:
            logger.error(
                "match_crawl_failed",
                match_id=match.get('_id'),
                error=str(e)
            )
            continue

    return {"matches_updated": matches_updated}


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
    Async implementation of match events crawling
    """
    db = get_mongo_db()
    service = MatchService(db)

    # Get current live matches
    live_matches = await service.get_live_matches(limit=100)

    if not live_matches:
        return {"events_found": 0}

    crawler = FlashScoreCrawler()
    events_found = 0

    for match in live_matches:
        try:
            external_id = match.get('external_id')
            if not external_id:
                continue

            # Crawl events
            events = await crawler.crawl_match_events(external_id)

            # Check for new events
            existing_events = match.get('events', [])
            existing_event_ids = {
                f"{e['type']}_{e['minute']}_{e['player']}"
                for e in existing_events
            }

            for event in events:
                event_id = f"{event['type']}_{event['minute']}_{event['player']}"

                if event_id not in existing_event_ids:
                    # New event found!
                    await service.add_match_event(str(match['_id']), event)
                    events_found += 1

                    # Publish event notification
                    await publish_match_event(str(match['_id']), event)

                    logger.info(
                        "new_match_event",
                        match_id=str(match['_id']),
                        event_type=event['type'],
                        minute=event['minute']
                    )

        except Exception as e:
            logger.error(
                "events_crawl_failed",
                match_id=match.get('_id'),
                error=str(e)
            )
            continue

    return {"events_found": events_found}


async def publish_match_update(match_id: str, data: dict):
    """
    Publish match update to Redis for WebSocket broadcasting
    """
    try:
        import redis.asyncio as redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        redis_client = await redis.from_url(redis_url)

        message = {
            "type": "match_update",
            "channel": f"match:{match_id}",
            "data": {
                "match_id": match_id,
                "score": data.get('score'),
                "minute": data.get('minute'),
                "status": data.get('status')
            }
        }

        import json
        await redis_client.publish(f"match:{match_id}", json.dumps(message))
        await redis_client.publish("live:all", json.dumps(message))

        await redis_client.close()

    except Exception as e:
        logger.error("publish_match_update_failed", error=str(e))


async def publish_match_event(match_id: str, event: dict):
    """
    Publish match event (goal, card) to Redis
    """
    try:
        import redis.asyncio as redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        redis_client = await redis.from_url(redis_url)

        message = {
            "type": event['type'],
            "channel": f"match:{match_id}",
            "data": {
                "match_id": match_id,
                **event
            }
        }

        import json
        await redis_client.publish(f"match:{match_id}", json.dumps(message))
        await redis_client.publish("live:all", json.dumps(message))

        await redis_client.close()

    except Exception as e:
        logger.error("publish_match_event_failed", error=str(e))
