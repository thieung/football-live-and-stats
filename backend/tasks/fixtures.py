"""
Celery tasks for fixture crawling
"""
from celery import shared_task
import structlog
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os

from crawlers.flashscore import FlashScoreCrawler
from crawlers.validators import validate_crawled_data
from api.services.match_service import MatchService

logger = structlog.get_logger()


def get_mongo_db():
    """Get MongoDB database connection"""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://admin:password123@mongodb:27017')
    mongo_db_name = os.getenv('MONGO_DB_NAME', 'football_live')
    client = AsyncIOMotorClient(mongo_uri)
    return client[mongo_db_name]


@shared_task(bind=True, max_retries=3)
def crawl_daily_fixtures(self):
    """
    Crawl upcoming fixtures for the next 7 days
    Runs daily at 2 AM
    """
    try:
        logger.info("crawl_daily_fixtures_started")

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(_crawl_fixtures_async())

        logger.info(
            "crawl_daily_fixtures_completed",
            fixtures_crawled=result.get('fixtures_crawled', 0)
        )

        return result

    except Exception as e:
        logger.error("crawl_daily_fixtures_failed", error=str(e))
        raise self.retry(exc=e, countdown=60)


async def _crawl_fixtures_async():
    """
    Async implementation of fixture crawling with database storage
    """
    db = get_mongo_db()
    service = MatchService(db)
    crawler = FlashScoreCrawler()

    # Crawl fixtures for next 7 days
    raw_fixtures = await crawler.crawl_fixtures(days_ahead=7)

    logger.info("fixtures_crawled_from_source", count=len(raw_fixtures))

    if not raw_fixtures:
        logger.warning("no_fixtures_found")
        return {
            "fixtures_crawled": 0,
            "fixtures_stored": 0,
            "duplicates_skipped": 0,
            "validation_errors": 0
        }

    fixtures_stored = 0
    duplicates_skipped = 0
    validation_errors = 0

    for fixture_data in raw_fixtures:
        try:
            # Extract external ID
            external_id = fixture_data.get('external_id')
            if not external_id:
                logger.warning("fixture_missing_external_id", fixture=fixture_data)
                continue

            # Check if fixture already exists
            existing = await service.get_match_by_external_id(external_id)
            if existing:
                duplicates_skipped += 1
                logger.debug("fixture_already_exists", external_id=external_id)
                continue

            # Validate fixture data (only if it has match info)
            if 'score' in fixture_data:
                validated_data = validate_crawled_data(fixture_data)
                if not validated_data:
                    validation_errors += 1
                    logger.error("fixture_validation_failed", fixture=fixture_data)
                    continue

            # Store fixture in database
            # Note: Fixtures typically don't have full match data yet,
            # so we store them as scheduled matches
            fixture_doc = {
                'external_id': external_id,
                'home_team': fixture_data.get('home_team'),
                'away_team': fixture_data.get('away_team'),
                'league': fixture_data.get('league'),
                'match_date': fixture_data.get('match_date'),
                'status': 'scheduled',
                'score': {'home': 0, 'away': 0},
                'events': [],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }

            await service.create_match(fixture_doc)
            fixtures_stored += 1

            logger.info(
                "fixture_stored",
                external_id=external_id,
                home_team=fixture_data.get('home_team', {}).get('name'),
                away_team=fixture_data.get('away_team', {}).get('name'),
                match_date=fixture_data.get('match_date')
            )

        except Exception as e:
            logger.error(
                "fixture_processing_failed",
                fixture=fixture_data,
                error=str(e),
                error_type=type(e).__name__
            )
            continue

    result = {
        "fixtures_crawled": len(raw_fixtures),
        "fixtures_stored": fixtures_stored,
        "duplicates_skipped": duplicates_skipped,
        "validation_errors": validation_errors
    }

    logger.info("crawl_fixtures_summary", **result)

    return result
