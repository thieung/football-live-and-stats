"""
Database Setup Verification Script

This script tests all database connections and verifies that:
- PostgreSQL is accessible and tables are created
- MongoDB is accessible and collections work
- Redis is accessible
- Seed data exists
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text, select
from api.core.database import AsyncSessionLocal, mongo_client, redis_client
from api.core.config import settings
from api.models.postgres import User, League, Team, Fixture
import structlog

logger = structlog.get_logger()


async def test_postgresql():
    """Test PostgreSQL connection and schema"""
    print("\n🔍 Testing PostgreSQL...")

    try:
        async with AsyncSessionLocal() as session:
            # Test basic connection
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            print("  ✅ PostgreSQL connection successful")

            # Check tables exist
            tables = ['users', 'leagues', 'teams', 'fixtures', 'user_favorites', 'crawl_jobs']
            for table in tables:
                result = await session.execute(
                    text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                )
                exists = result.scalar()
                if exists:
                    print(f"  ✅ Table '{table}' exists")
                else:
                    print(f"  ❌ Table '{table}' does NOT exist")
                    return False

            # Check seed data
            leagues_result = await session.execute(select(League))
            leagues_count = len(leagues_result.scalars().all())
            print(f"  ℹ️  Found {leagues_count} leagues")

            teams_result = await session.execute(select(Team))
            teams_count = len(teams_result.scalars().all())
            print(f"  ℹ️  Found {teams_count} teams")

            fixtures_result = await session.execute(select(Fixture))
            fixtures_count = len(fixtures_result.scalars().all())
            print(f"  ℹ️  Found {fixtures_count} fixtures")

            if leagues_count > 0 and teams_count > 0:
                print("  ✅ Seed data exists")
            else:
                print("  ⚠️  No seed data found - run 'python scripts/seed_data.py'")

            return True

    except Exception as e:
        print(f"  ❌ PostgreSQL test failed: {e}")
        return False


async def test_mongodb():
    """Test MongoDB connection and collections"""
    print("\n🔍 Testing MongoDB...")

    try:
        # Test connection
        await mongo_client.admin.command('ping')
        print("  ✅ MongoDB connection successful")

        # Get database
        db = mongo_client[settings.MONGO_DB_NAME]
        print(f"  ✅ Using database: {settings.MONGO_DB_NAME}")

        # Test matches collection
        matches_count = await db.matches.count_documents({})
        print(f"  ℹ️  Found {matches_count} matches")

        if matches_count > 0:
            print("  ✅ Match data exists")
            # Get a sample match
            sample_match = await db.matches.find_one()
            if sample_match:
                print(f"  ℹ️  Sample match: {sample_match.get('external_id', 'N/A')}")
        else:
            print("  ⚠️  No match data found - run 'python scripts/seed_data.py'")

        # Check indexes
        indexes = await db.matches.index_information()
        print(f"  ℹ️  Indexes: {', '.join(indexes.keys())}")

        return True

    except Exception as e:
        print(f"  ❌ MongoDB test failed: {e}")
        return False


async def test_redis():
    """Test Redis connection"""
    print("\n🔍 Testing Redis...")

    try:
        # Test connection
        pong = await redis_client.ping()
        if pong:
            print("  ✅ Redis connection successful")
        else:
            print("  ❌ Redis ping failed")
            return False

        # Test set/get
        test_key = "test:setup"
        await redis_client.set(test_key, "test_value", ex=10)
        value = await redis_client.get(test_key)

        if value == "test_value":
            print("  ✅ Redis read/write successful")
            await redis_client.delete(test_key)
        else:
            print("  ❌ Redis read/write failed")
            return False

        # Get info
        info = await redis_client.info()
        version = info.get('redis_version', 'unknown')
        print(f"  ℹ️  Redis version: {version}")

        return True

    except Exception as e:
        print(f"  ❌ Redis test failed: {e}")
        return False


async def test_all():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Football Live Score - Database Setup Verification")
    print("=" * 60)

    results = {
        'postgresql': await test_postgresql(),
        'mongodb': await test_mongodb(),
        'redis': await test_redis(),
    }

    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    all_passed = all(results.values())

    for service, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{service.upper():12s}: {status}")

    print("=" * 60)

    if all_passed:
        print("\n✅ All tests passed! Database setup is complete.")
        print("\nNext steps:")
        print("  1. Start the backend: uvicorn api.main:app --reload")
        print("  2. Start Celery worker: celery -A tasks.celery_app worker --loglevel=info")
        print("  3. Start frontend: cd ../frontend && npm run dev")
        print("  4. Visit API docs: http://localhost:8000/api/v1/docs")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        if not results['postgresql']:
            print("  - PostgreSQL: Check connection string in .env")
            print("  - Run migrations: alembic upgrade head")
        if not results['mongodb']:
            print("  - MongoDB: Check connection string in .env")
            print("  - Ensure MongoDB is running")
        if not results['redis']:
            print("  - Redis: Check if Redis server is running")
            print("  - Try: redis-cli ping")

    # Cleanup
    mongo_client.close()
    await redis_client.close()

    return 0 if all_passed else 1


def main():
    """Entry point"""
    try:
        exit_code = asyncio.run(test_all())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
