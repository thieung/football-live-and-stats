"""
Database Setup Script

This script automates the entire database setup process:
1. Checks if Docker services are running
2. Runs Alembic migrations
3. Seeds initial data
4. Verifies the setup

Usage:
    python scripts/setup_database.py [--skip-docker-check] [--skip-seed]
"""
import asyncio
import sys
import subprocess
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

import structlog

logger = structlog.get_logger()


def check_docker_services():
    """Check if required Docker services are running"""
    print("\n🔍 Checking Docker services...")

    required_services = ['football_postgres', 'football_mongodb', 'football_redis']
    all_running = True

    try:
        result = subprocess.run(
            ['docker', 'ps', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            check=True
        )
        running_containers = result.stdout.strip().split('\n')

        for service in required_services:
            if service in running_containers:
                print(f"  ✅ {service} is running")
            else:
                print(f"  ❌ {service} is NOT running")
                all_running = False

        if not all_running:
            print("\n⚠️  Some services are not running.")
            print("    Run: docker-compose up -d postgres mongodb redis")
            print("    Or: cd backend && docker compose up -d postgres mongodb redis")
            return False

        print("  ✅ All required Docker services are running")
        return True

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Error checking Docker: {e}")
        print("    Make sure Docker is installed and running")
        return False
    except FileNotFoundError:
        print("  ⚠️  Docker command not found")
        print("    Skipping Docker check (use --skip-docker-check if services are running)")
        return False


def run_migrations():
    """Run Alembic migrations"""
    print("\n🔄 Running database migrations...")

    try:
        # Change to backend directory
        backend_dir = Path(__file__).parent.parent

        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            cwd=backend_dir,
            capture_output=True,
            text=True,
            check=True
        )

        print("  ✅ Migrations completed successfully")
        if result.stdout:
            print(f"  ℹ️  {result.stdout.strip()}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Migration failed: {e}")
        if e.stderr:
            print(f"     Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("  ❌ Alembic command not found")
        print("     Install dependencies: pip install -r requirements.txt")
        return False


async def seed_database():
    """Seed initial data"""
    print("\n🌱 Seeding database with initial data...")

    try:
        # Import and run seed script
        from seed_data import main as seed_main

        await seed_main()
        print("  ✅ Database seeded successfully")
        return True

    except Exception as e:
        print(f"  ❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def verify_setup():
    """Verify database setup"""
    print("\n🔍 Verifying database setup...")

    try:
        # Import and run test script
        from test_setup import test_all

        result = await test_all()
        return result == 0

    except Exception as e:
        print(f"  ❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the full setup process"""
    parser = argparse.ArgumentParser(description='Setup Football Live Score database')
    parser.add_argument('--skip-docker-check', action='store_true',
                       help='Skip Docker services check')
    parser.add_argument('--skip-seed', action='store_true',
                       help='Skip seeding data (only run migrations)')

    args = parser.parse_args()

    print("=" * 70)
    print("🚀 Football Live Score - Database Setup")
    print("=" * 70)

    # Step 1: Check Docker services (optional)
    if not args.skip_docker_check:
        if not check_docker_services():
            print("\n❌ Setup aborted: Docker services not ready")
            print("   Use --skip-docker-check to bypass this check")
            return 1
    else:
        print("\n⚠️  Skipping Docker check (--skip-docker-check)")

    # Step 2: Run migrations
    if not run_migrations():
        print("\n❌ Setup aborted: Migration failed")
        return 1

    # Step 3: Seed data (optional)
    if not args.skip_seed:
        if not await seed_database():
            print("\n⚠️  Warning: Seeding failed, but continuing...")
    else:
        print("\n⚠️  Skipping data seeding (--skip-seed)")

    # Step 4: Verify setup
    if not await verify_setup():
        print("\n⚠️  Warning: Verification had some issues")
        print("   Check the errors above and run 'python scripts/test_setup.py' manually")

    print("\n" + "=" * 70)
    print("✅ Database setup completed!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Create .env file: cp .env.example .env")
    print("  2. Update .env with your settings")
    print("  3. Start the backend:")
    print("     uvicorn api.main:app --reload")
    print("  4. Start Celery worker:")
    print("     celery -A tasks.celery_app worker --loglevel=info")
    print("  5. Visit API docs:")
    print("     http://localhost:8000/api/v1/docs")
    print()

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
