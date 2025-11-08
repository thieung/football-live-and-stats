"""
League service for business logic
"""
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

logger = structlog.get_logger()


class LeagueService:
    """Service for league-related operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.league_tables = db.league_tables
        self.matches = db.matches

    async def get_league_table(self, league_id: str, season: str) -> Optional[dict]:
        """
        Get league standings/table
        """
        table = await self.league_tables.find_one({
            "league_id": league_id,
            "season": season
        })

        return table

    async def update_league_table(self, league_id: str, season: str, standings: List[dict]) -> bool:
        """
        Update league standings
        """
        from datetime import datetime

        result = await self.league_tables.update_one(
            {
                "league_id": league_id,
                "season": season
            },
            {
                "$set": {
                    "standings": standings,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

        logger.info("league_table_updated", league_id=league_id, season=season)
        return True

    async def get_league_fixtures(self, league_id: str, limit: int = 50) -> List[dict]:
        """
        Get league fixtures
        """
        matches = await self.matches.find(
            {"league.id": league_id}
        ).sort("match_date", -1).limit(limit).to_list(limit)

        return matches
