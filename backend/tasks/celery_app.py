"""
Celery application configuration
"""
from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Create Celery app
app = Celery(
    'football_live',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/2'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2'),
    include=[
        'tasks.live_scores',
        'tasks.fixtures',
        'tasks.stats'
    ]
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,  # 4 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Crawl live scores every 30 seconds
    'crawl-live-scores': {
        'task': 'tasks.live_scores.crawl_live_scores',
        'schedule': 30.0,
    },

    # Crawl match events every 10 seconds (high priority)
    'crawl-match-events': {
        'task': 'tasks.live_scores.crawl_match_events',
        'schedule': 10.0,
    },

    # Crawl fixtures daily at 2 AM
    'crawl-daily-fixtures': {
        'task': 'tasks.fixtures.crawl_daily_fixtures',
        'schedule': crontab(hour=2, minute=0),
    },

    # Crawl league tables every hour
    'crawl-league-tables': {
        'task': 'tasks.stats.crawl_league_tables',
        'schedule': crontab(minute=0),
    },

    # Update team statistics every 6 hours
    'update-team-stats': {
        'task': 'tasks.stats.update_team_stats',
        'schedule': crontab(minute=0, hour='*/6'),
    },
}

if __name__ == '__main__':
    app.start()
