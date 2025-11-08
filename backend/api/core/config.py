"""
Configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Application
    APP_NAME: str = "Football Live Score API"
    DEBUG: bool = False
    SECRET_KEY: str
    API_VERSION: str = "v1"

    # Database - PostgreSQL
    DATABASE_URL: str

    # Database - MongoDB
    MONGO_URI: str
    MONGO_DB_NAME: str = "football_live"

    # Redis
    REDIS_URL: str
    REDIS_CACHE_DB: int = 1
    REDIS_CELERY_DB: int = 2

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173"]

    # Crawling
    CRAWL_LIVE_SCORES_INTERVAL: int = 30
    CRAWL_MATCH_EVENTS_INTERVAL: int = 10
    CRAWL_FIXTURES_HOUR: int = 2
    CRAWL_LEAGUE_TABLES_INTERVAL: int = 3600

    # Proxy
    USE_PROXY: bool = False
    PROXY_PROVIDER: str = "scraperapi"
    PROXY_API_KEY: str = ""

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
