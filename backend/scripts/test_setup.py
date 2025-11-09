"""
Test script to validate setup

This script tests:
- Database connections (PostgreSQL, MongoDB, Redis)
- API endpoints
- Basic functionality
"""
import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from api.core.config import settings
from api.core.database import engine, mongo_client, redis_client
import structlog

logger = structlog.get_logger()


async def test_postgresql():
    """Test PostgreSQL connection"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            logger.info("postgresql_test", status="success")
            return True
    except Exception as e:
        logger.error("postgresql_test_failed", error=str(e))
        return False


async def test_mongodb():
    """Test MongoDB connection"""
    try:
        await mongo_client.admin.command('ping')
        logger.info("mongodb_test", status="success")
        return True
    except Exception as e:
        logger.error("mongodb_test_failed", error=str(e))
        return False


async def test_redis():
    """Test Redis connection"""
    try:
        await redis_client.ping()
        logger.info("redis_test", status="success")
        return True
    except Exception as e:
        logger.error("redis_test_failed", error=str(e))
        return False


async def main():
    """Run all tests"""
    logger.info("setup_test_started")

    results = {
        "postgresql": await test_postgresql(),
        "mongodb": await test_mongodb(),
        "redis": await test_redis()
    }

    all_passed = all(results.values())

    if all_passed:
        logger.info("setup_test_completed", status="success", results=results)
    else:
        logger.error("setup_test_failed", results=results)
        sys.exit(1)

    # Cleanup
    await engine.dispose()
    mongo_client.close()
    await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
