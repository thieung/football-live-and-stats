"""
Data validation and transformation for crawled data

This module handles:
- Validation of crawled data
- Transformation from crawler format to database format
- Data sanitization and normalization
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
import structlog

logger = structlog.get_logger()


class CrawledScore(BaseModel):
    """Validated score data from crawler"""
    home: int = Field(ge=0, le=99)
    away: int = Field(ge=0, le=99)


class CrawledEvent(BaseModel):
    """Validated event data from crawler"""
    type: str = Field(..., description="Event type: goal, yellow_card, red_card, substitution")
    minute: int = Field(..., ge=0, le=200)  # Including extra time
    player: str = Field(..., min_length=1, max_length=200)
    team: str = Field(..., regex='^(home|away)$')
    assist: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=500)

    @validator('type')
    def validate_event_type(cls, v):
        """Validate event type"""
        valid_types = ['goal', 'yellow_card', 'red_card', 'substitution', 'penalty', 'own_goal']
        if v not in valid_types:
            logger.warning("invalid_event_type", type=v)
            # Default to goal if unknown
            return 'goal'
        return v

    @validator('player', 'assist')
    def clean_player_name(cls, v):
        """Clean and normalize player names"""
        if v:
            # Remove extra whitespace
            v = ' '.join(v.split())
            # Capitalize properly
            v = v.strip()
        return v


class CrawledStatistics(BaseModel):
    """Validated statistics data from crawler"""
    possession: Optional[Dict[str, int]] = None
    shots: Optional[Dict[str, int]] = None
    shots_on_target: Optional[Dict[str, int]] = None
    corners: Optional[Dict[str, int]] = None
    fouls: Optional[Dict[str, int]] = None
    yellow_cards: Optional[Dict[str, int]] = None
    red_cards: Optional[Dict[str, int]] = None

    @validator('*', pre=True)
    def validate_team_stats(cls, v):
        """Validate team statistics have both home and away"""
        if v is not None and isinstance(v, dict):
            # Ensure we have both home and away keys
            if 'home' not in v:
                v['home'] = 0
            if 'away' not in v:
                v['away'] = 0
            # Ensure values are non-negative
            v['home'] = max(0, v['home'])
            v['away'] = max(0, v['away'])
        return v


class CrawledMatchData(BaseModel):
    """Complete validated match data from crawler"""
    score: CrawledScore
    minute: Optional[int] = Field(None, ge=0, le=200)
    status: str = Field(..., description="Match status: scheduled, live, halftime, finished")
    events: List[CrawledEvent] = []
    statistics: Optional[CrawledStatistics] = None

    @validator('status')
    def validate_status(cls, v):
        """Validate and normalize match status"""
        valid_statuses = ['scheduled', 'live', 'halftime', 'finished', 'postponed', 'cancelled']
        v_lower = v.lower()

        # Map common variations to standard statuses
        status_map = {
            'ft': 'finished',
            'finished': 'finished',
            'live': 'live',
            'in play': 'live',
            'ht': 'halftime',
            'half-time': 'halftime',
            'halftime': 'halftime',
            'scheduled': 'scheduled',
            'not started': 'scheduled',
            'postponed': 'postponed',
            'cancelled': 'cancelled',
            'abandoned': 'cancelled',
        }

        normalized = status_map.get(v_lower)
        if not normalized:
            logger.warning("unknown_status", status=v)
            return 'scheduled'

        return normalized

    @validator('events')
    def sort_events_by_minute(cls, v):
        """Sort events by minute"""
        if v:
            return sorted(v, key=lambda e: e.minute)
        return v


class CrawlDataTransformer:
    """
    Transforms validated crawler data to database format
    """

    @staticmethod
    def transform_match_data(
        crawled_data: CrawledMatchData,
        existing_match: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Transform crawled match data to database format

        Args:
            crawled_data: Validated crawled data
            existing_match: Existing match data from database (if any)

        Returns:
            Dictionary ready for database insertion/update
        """
        now = datetime.utcnow()

        # Build update data
        update_data = {
            'score': {
                'home': crawled_data.score.home,
                'away': crawled_data.score.away,
            },
            'status': crawled_data.status,
            'updated_at': now,
        }

        # Add minute if provided
        if crawled_data.minute is not None:
            update_data['minute'] = crawled_data.minute

        # Add statistics if provided
        if crawled_data.statistics:
            update_data['statistics'] = crawled_data.statistics.dict(exclude_none=True)

        # Handle events - merge with existing to avoid duplicates
        if crawled_data.events:
            events_dict = [event.dict(exclude_none=True) for event in crawled_data.events]

            if existing_match and 'events' in existing_match:
                # Merge new events with existing
                update_data['events'] = CrawlDataTransformer._merge_events(
                    existing_match['events'],
                    events_dict
                )
            else:
                update_data['events'] = events_dict

        # Update halftime score if status is halftime or finished
        if crawled_data.status in ['halftime', 'finished'] and existing_match:
            if not existing_match.get('score', {}).get('halftime'):
                # Record halftime score if not already recorded
                if crawled_data.status == 'halftime':
                    update_data.setdefault('score', {})['halftime'] = {
                        'home': crawled_data.score.home,
                        'away': crawled_data.score.away,
                    }

        # Update fulltime score if status is finished
        if crawled_data.status == 'finished':
            update_data.setdefault('score', {})['fulltime'] = {
                'home': crawled_data.score.home,
                'away': crawled_data.score.away,
            }

        logger.debug(
            "match_data_transformed",
            status=crawled_data.status,
            score=update_data['score'],
            events_count=len(update_data.get('events', []))
        )

        return update_data

    @staticmethod
    def _merge_events(
        existing_events: List[Dict],
        new_events: List[Dict]
    ) -> List[Dict]:
        """
        Merge new events with existing events, avoiding duplicates

        Duplicate detection based on: type + minute + player + team
        """
        # Create set of existing event signatures
        existing_signatures = {
            f"{e['type']}_{e['minute']}_{e['player']}_{e['team']}"
            for e in existing_events
        }

        # Merge events
        merged = list(existing_events)

        for event in new_events:
            signature = f"{event['type']}_{event['minute']}_{event['player']}_{event['team']}"

            if signature not in existing_signatures:
                merged.append(event)
                existing_signatures.add(signature)
                logger.info(
                    "new_event_detected",
                    type=event['type'],
                    minute=event['minute'],
                    player=event['player']
                )

        # Sort by minute
        return sorted(merged, key=lambda e: e['minute'])


def validate_crawled_data(raw_data: Dict[str, Any]) -> Optional[CrawledMatchData]:
    """
    Validate raw crawled data

    Args:
        raw_data: Raw data from crawler

    Returns:
        Validated CrawledMatchData or None if validation fails
    """
    try:
        validated = CrawledMatchData(**raw_data)
        logger.debug("data_validation_success", status=validated.status)
        return validated

    except Exception as e:
        logger.error(
            "data_validation_failed",
            error=str(e),
            raw_data=raw_data
        )
        return None


def transform_for_database(
    raw_data: Dict[str, Any],
    existing_match: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Complete pipeline: validate and transform crawler data for database

    Args:
        raw_data: Raw data from crawler
        existing_match: Existing match data (if any)

    Returns:
        Database-ready dictionary or None if validation fails
    """
    # Step 1: Validate
    validated = validate_crawled_data(raw_data)
    if not validated:
        return None

    # Step 2: Transform
    transformed = CrawlDataTransformer.transform_match_data(validated, existing_match)

    return transformed
