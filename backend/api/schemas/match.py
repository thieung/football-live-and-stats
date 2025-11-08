"""
Pydantic schemas for Match-related operations
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class TeamBasic(BaseModel):
    """Basic team info"""
    id: UUID
    name: str
    short_name: Optional[str] = None
    logo: Optional[str] = None


class LeagueBasic(BaseModel):
    """Basic league info"""
    id: UUID
    name: str
    country: Optional[str] = None
    logo: Optional[str] = None


class Score(BaseModel):
    """Match score"""
    home: Optional[int] = None
    away: Optional[int] = None


class MatchScore(BaseModel):
    """Complete match score"""
    home: int = 0
    away: int = 0
    halftime: Optional[Score] = None
    fulltime: Optional[Score] = None
    extra_time: Optional[Score] = None
    penalty: Optional[Score] = None


class MatchEvent(BaseModel):
    """Match event (goal, card, substitution)"""
    type: str  # goal, yellow_card, red_card, substitution
    minute: int
    player: str
    team: str  # home or away
    assist: Optional[str] = None
    description: Optional[str] = None


class MatchStatistics(BaseModel):
    """Match statistics"""
    possession: Optional[Dict[str, int]] = None
    shots: Optional[Dict[str, int]] = None
    shots_on_target: Optional[Dict[str, int]] = None
    corners: Optional[Dict[str, int]] = None
    fouls: Optional[Dict[str, int]] = None
    yellow_cards: Optional[Dict[str, int]] = None
    red_cards: Optional[Dict[str, int]] = None


class MatchResponse(BaseModel):
    """Match response schema"""
    id: str = Field(..., alias="_id")
    external_id: str
    fixture_id: Optional[UUID] = None
    league: LeagueBasic
    home_team: TeamBasic
    away_team: TeamBasic
    match_date: datetime
    status: str  # scheduled, live, halftime, finished
    minute: Optional[int] = None
    score: MatchScore
    events: List[MatchEvent] = []
    statistics: Optional[MatchStatistics] = None
    updated_at: datetime

    class Config:
        populate_by_name = True


class MatchListItem(BaseModel):
    """Match list item (simplified)"""
    id: str = Field(..., alias="_id")
    home_team: TeamBasic
    away_team: TeamBasic
    match_date: datetime
    status: str
    minute: Optional[int] = None
    score: MatchScore

    class Config:
        populate_by_name = True


class MatchQuery(BaseModel):
    """Match query parameters"""
    league_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    date: Optional[datetime] = None
    status: Optional[str] = None
    limit: int = Field(50, le=100)
    offset: int = 0
