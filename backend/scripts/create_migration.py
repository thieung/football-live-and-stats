"""
Create initial Alembic migration

Usage:
    python scripts/create_migration.py

This will generate an initial migration based on the current models.
"""
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))


def create_migration():
    """Generate initial migration using Alembic"""
    try:
        # Run alembic revision with autogenerate
        result = subprocess.run(
            [
                "alembic",
                "revision",
                "--autogenerate",
                "-m",
                "initial_schema"
            ],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print("✅ Migration created successfully!")
            print(result.stdout)
        else:
            print("❌ Migration creation failed!")
            print(result.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_migration()
