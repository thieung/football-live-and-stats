"""
Match service for business logic
"""
from typing import List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import structlog

logger = structlog.get_logger()


class MatchService:
    """Service for match-related operations"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.matches = db.matches

    async def get_live_matches(self, limit: int = 50) -> List[dict]:
        """
        Get all live matches
        """
        matches = await self.matches.find(
            {"status": "live"}
        ).sort("match_date", -1).limit(limit).to_list(limit)

        return matches

    async def get_matches_by_date(self, date: datetime.date, limit: int = 100) -> List[dict]:
        """
        Get matches by date
        """
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())

        matches = await self.matches.find(
            {
                "match_date": {
                    "$gte": start_of_day,
                    "$lte": end_of_day
                }
            }
        ).sort("match_date", 1).limit(limit).to_list(limit)

        return matches

    async def get_upcoming_matches(self, days: int = 7, limit: int = 100) -> List[dict]:
        """
        Get upcoming matches
        """
        now = datetime.utcnow()
        end_date = now + timedelta(days=days)

        matches = await self.matches.find(
            {
                "match_date": {
                    "$gte": now,
                    "$lte": end_date
                },
                "status": "scheduled"
            }
        ).sort("match_date", 1).limit(limit).to_list(limit)

        return matches

    async def get_match_by_id(self, match_id: str) -> Optional[dict]:
        """
        Get match by ID
        """
        try:
            match = await self.matches.find_one({"_id": match_id})
            return match
        except Exception as e:
            logger.error("get_match_failed", match_id=match_id, error=str(e))
            return None

    async def get_match_by_external_id(self, external_id: str) -> Optional[dict]:
        """
        Get match by external ID (from crawl source)
        """
        match = await self.matches.find_one({"external_id": external_id})
        return match

    async def create_match(self, match_data: dict) -> dict:
        """
        Create new match
        """
        result = await self.matches.insert_one(match_data)
        match_data["_id"] = result.inserted_id
        logger.info("match_created", match_id=str(result.inserted_id))
        return match_data

    async def update_match(self, match_id: str, update_data: dict) -> bool:
        """
        Update match data
        """
        update_data["updated_at"] = datetime.utcnow()

        result = await self.matches.update_one(
            {"_id": match_id},
            {"$set": update_data}
        )

        if result.modified_count > 0:
            logger.info("match_updated", match_id=match_id)
            return True

        return False

    async def update_match_score(self, match_id: str, score: dict, minute: int = None) -> bool:
        """
        Update match score (for live updates)
        """
        update_data = {
            "score": score,
            "updated_at": datetime.utcnow()
        }

        if minute is not None:
            update_data["minute"] = minute

        result = await self.matches.update_one(
            {"_id": match_id},
            {"$set": update_data}
        )

        return result.modified_count > 0

    async def add_match_event(self, match_id: str, event: dict) -> bool:
        """
        Add event to match (goal, card, etc.)
        """
        result = await self.matches.update_one(
            {"_id": match_id},
            {
                "$push": {"events": event},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

        if result.modified_count > 0:
            logger.info("match_event_added", match_id=match_id, event_type=event.get("type"))
            return True

        return False
