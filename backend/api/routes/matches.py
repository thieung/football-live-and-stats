"""
Matches routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID
import structlog

from api.core.database import get_mongo_db
from api.services.match_service import MatchService
from api.schemas.match import MatchResponse, MatchListItem

logger = structlog.get_logger()
router = APIRouter()


@router.get("/live", response_model=List[MatchListItem])
async def get_live_matches(
    limit: int = Query(50, le=100),
    db = Depends(get_mongo_db)
):
    """
    Get all live matches
    """
    service = MatchService(db)
    matches = await service.get_live_matches(limit=limit)
    return matches


@router.get("/today", response_model=List[MatchListItem])
async def get_today_matches(
    limit: int = Query(100, le=200),
    db = Depends(get_mongo_db)
):
    """
    Get today's matches
    """
    service = MatchService(db)
    matches = await service.get_matches_by_date(datetime.utcnow().date(), limit=limit)
    return matches


@router.get("/upcoming", response_model=List[MatchListItem])
async def get_upcoming_matches(
    days: int = Query(7, le=30),
    limit: int = Query(100, le=200),
    db = Depends(get_mongo_db)
):
    """
    Get upcoming matches
    """
    service = MatchService(db)
    matches = await service.get_upcoming_matches(days=days, limit=limit)
    return matches


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match_details(
    match_id: str,
    db = Depends(get_mongo_db)
):
    """
    Get detailed match information
    """
    service = MatchService(db)
    match = await service.get_match_by_id(match_id)

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    return match


@router.get("/{match_id}/events")
async def get_match_events(
    match_id: str,
    db = Depends(get_mongo_db)
):
    """
    Get match events timeline
    """
    service = MatchService(db)
    match = await service.get_match_by_id(match_id)

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    return {
        "match_id": match_id,
        "events": match.get("events", [])
    }


@router.get("/{match_id}/stats")
async def get_match_statistics(
    match_id: str,
    db = Depends(get_mongo_db)
):
    """
    Get match statistics
    """
    service = MatchService(db)
    match = await service.get_match_by_id(match_id)

    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found"
        )

    return {
        "match_id": match_id,
        "statistics": match.get("statistics", {})
    }
