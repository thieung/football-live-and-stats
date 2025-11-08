"""
Celery tasks for fixture crawling
"""
from celery import shared_task
import structlog
import asyncio
from datetime import datetime, timedelta

from crawlers.flashscore import FlashScoreCrawler

logger = structlog.get_logger()


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
    Async implementation of fixture crawling
    """
    crawler = FlashScoreCrawler()

    # Crawl fixtures for next 7 days
    fixtures = await crawler.crawl_fixtures(days_ahead=7)

    logger.info("fixtures_crawled", count=len(fixtures))

    # TODO: Store fixtures in database
    # This will be implemented when we have the full crawler

    return {"fixtures_crawled": len(fixtures)}
