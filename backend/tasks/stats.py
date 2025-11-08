"""
Celery tasks for statistics crawling
"""
from celery import shared_task
import structlog
import asyncio

from crawlers.flashscore import FlashScoreCrawler

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3)
def crawl_league_tables(self):
    """
    Crawl league standings/tables
    Runs every hour
    """
    try:
        logger.info("crawl_league_tables_started")

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(_crawl_league_tables_async())

        logger.info(
            "crawl_league_tables_completed",
            tables_updated=result.get('tables_updated', 0)
        )

        return result

    except Exception as e:
        logger.error("crawl_league_tables_failed", error=str(e))
        raise self.retry(exc=e, countdown=300)


async def _crawl_league_tables_async():
    """
    Async implementation of league tables crawling
    """
    crawler = FlashScoreCrawler()

    # TODO: Get list of active leagues from database
    # For now, we'll use hardcoded major leagues

    major_leagues = [
        'premier-league',
        'la-liga',
        'bundesliga',
        'serie-a',
        'ligue-1'
    ]

    tables_updated = 0

    for league in major_leagues:
        try:
            table = await crawler.crawl_league_table(league)

            if table:
                # TODO: Store table in database
                tables_updated += 1
                logger.info("league_table_crawled", league=league)

        except Exception as e:
            logger.error("league_table_crawl_failed", league=league, error=str(e))
            continue

    return {"tables_updated": tables_updated}


@shared_task(bind=True, max_retries=3)
def update_team_stats(self):
    """
    Update team statistics
    Runs every 6 hours
    """
    try:
        logger.info("update_team_stats_started")

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        result = loop.run_until_complete(_update_team_stats_async())

        logger.info(
            "update_team_stats_completed",
            teams_updated=result.get('teams_updated', 0)
        )

        return result

    except Exception as e:
        logger.error("update_team_stats_failed", error=str(e))
        raise self.retry(exc=e, countdown=300)


async def _update_team_stats_async():
    """
    Async implementation of team stats update
    """
    # TODO: Implement team stats crawling
    logger.info("team_stats_update_placeholder")
    return {"teams_updated": 0}
