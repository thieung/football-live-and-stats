"""
Database configuration and connection management
Supports both PostgreSQL (SQLAlchemy) and MongoDB (Motor)
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis
from typing import AsyncGenerator
import structlog

from api.core.config import settings

logger = structlog.get_logger()

# SQLAlchemy Base
Base = declarative_base()

# PostgreSQL Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# MongoDB Client
mongo_client: AsyncIOMotorClient = None
mongo_db = None

# Redis Client
redis_client: redis.Redis = None
redis_cache_client: redis.Redis = None


async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get PostgreSQL database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_mongo_db():
    """
    Get MongoDB database instance
    """
    return mongo_db


def get_redis():
    """
    Get Redis client
    """
    return redis_client


def get_redis_cache():
    """
    Get Redis cache client
    """
    return redis_cache_client


async def init_db():
    """
    Initialize database connections on startup
    """
    global mongo_client, mongo_db, redis_client, redis_cache_client

    # Initialize MongoDB
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
        mongo_db = mongo_client[settings.MONGO_DB_NAME]

        # Test connection
        await mongo_client.admin.command('ping')
        logger.info("mongodb_connected", database=settings.MONGO_DB_NAME)

        # Create indexes
        await create_mongo_indexes()

    except Exception as e:
        logger.error("mongodb_connection_failed", error=str(e))
        raise

    # Initialize Redis
    try:
        redis_client = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )

        redis_cache_client = await redis.from_url(
            settings.REDIS_URL.replace("/0", f"/{settings.REDIS_CACHE_DB}"),
            encoding="utf-8",
            decode_responses=True
        )

        # Test connection
        await redis_client.ping()
        logger.info("redis_connected")

    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))
        raise

    # Create PostgreSQL tables
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("postgres_tables_created")
    except Exception as e:
        logger.error("postgres_setup_failed", error=str(e))
        raise


async def close_db():
    """
    Close database connections on shutdown
    """
    global mongo_client, redis_client, redis_cache_client

    # Close MongoDB
    if mongo_client:
        mongo_client.close()
        logger.info("mongodb_disconnected")

    # Close Redis
    if redis_client:
        await redis_client.close()
    if redis_cache_client:
        await redis_cache_client.close()
    logger.info("redis_disconnected")

    # Close PostgreSQL
    await engine.dispose()
    logger.info("postgres_disconnected")


async def create_mongo_indexes():
    """
    Create MongoDB indexes for optimal query performance
    """
    db = mongo_db

    # Matches collection indexes
    await db.matches.create_index([("status", 1), ("match_date", -1)])
    await db.matches.create_index([("league.id", 1), ("match_date", -1)])
    await db.matches.create_index([("home_team.id", 1)])
    await db.matches.create_index([("away_team.id", 1)])
    await db.matches.create_index([("external_id", 1)], unique=True)

    # League tables indexes
    await db.league_tables.create_index([("league_id", 1), ("season", 1)], unique=True)

    # Player stats indexes
    await db.player_stats.create_index([("player_id", 1), ("season", 1), ("league_id", 1)])

    logger.info("mongodb_indexes_created")
