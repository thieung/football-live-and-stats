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

    async def upsert_match(self, external_id: str, match_data: dict) -> tuple[dict, bool]:
        """
        Insert or update match based on external_id (from crawler)

        Args:
            external_id: External match ID from crawl source
            match_data: Match data to insert/update

        Returns:
            Tuple of (match_dict, is_new)
            - match_dict: The resulting match document
            - is_new: True if new match was created, False if updated
        """
        # Check if match exists
        existing_match = await self.get_match_by_external_id(external_id)

        if existing_match:
            # Update existing match
            match_id = str(existing_match['_id'])

            # Add updated timestamp
            match_data['updated_at'] = datetime.utcnow()

            # Update the match
            result = await self.matches.update_one(
                {"_id": existing_match['_id']},
                {"$set": match_data}
            )

            if result.modified_count > 0:
                logger.info(
                    "match_updated_from_crawler",
                    match_id=match_id,
                    external_id=external_id,
                    status=match_data.get('status')
                )

            # Fetch updated match
            updated_match = await self.get_match_by_id(existing_match['_id'])
            return updated_match, False

        else:
            # Create new match
            match_data['external_id'] = external_id
            match_data['created_at'] = datetime.utcnow()
            match_data['updated_at'] = datetime.utcnow()

            # Set defaults if not provided
            if 'events' not in match_data:
                match_data['events'] = []
            if 'status' not in match_data:
                match_data['status'] = 'scheduled'

            result = await self.matches.insert_one(match_data)
            match_data['_id'] = result.inserted_id

            logger.info(
                "match_created_from_crawler",
                match_id=str(result.inserted_id),
                external_id=external_id,
                status=match_data.get('status')
            )

            return match_data, True

    async def detect_duplicate_match(
        self,
        home_team: str,
        away_team: str,
        match_date: datetime,
        tolerance_hours: int = 3
    ) -> Optional[dict]:
        """
        Detect duplicate match by team names and date

        Args:
            home_team: Home team name
            away_team: Away team name
            match_date: Match date/time
            tolerance_hours: Time tolerance in hours for matching

        Returns:
            Existing match if found, None otherwise
        """
        from datetime import timedelta

        # Create time window
        start_time = match_date - timedelta(hours=tolerance_hours)
        end_time = match_date + timedelta(hours=tolerance_hours)

        # Query for potential duplicates
        potential_duplicates = await self.matches.find({
            "home_team.name": home_team,
            "away_team.name": away_team,
            "match_date": {
                "$gte": start_time,
                "$lte": end_time
            }
        }).to_list(10)

        if potential_duplicates:
            logger.warning(
                "duplicate_match_detected",
                home_team=home_team,
                away_team=away_team,
                count=len(potential_duplicates)
            )
            return potential_duplicates[0]

        return None

    async def get_matches_requiring_updates(self, limit: int = 100) -> List[dict]:
        """
        Get matches that need crawling updates (live or upcoming today)

        Returns:
            List of matches that should be crawled for updates
        """
        now = datetime.utcnow()
        today_start = datetime.combine(now.date(), datetime.min.time())
        today_end = datetime.combine(now.date(), datetime.max.time())

        # Get live matches and today's scheduled matches
        matches = await self.matches.find({
            "$or": [
                {"status": "live"},
                {"status": "halftime"},
                {
                    "status": "scheduled",
                    "match_date": {
                        "$gte": today_start,
                        "$lte": today_end
                    }
                }
            ]
        }).sort("match_date", 1).limit(limit).to_list(limit)

        logger.info("matches_requiring_updates_found", count=len(matches))

        return matches
