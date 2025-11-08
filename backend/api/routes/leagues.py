"""
Leagues routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from api.core.database import get_postgres_session, get_mongo_db
from api.models.postgres import League
from api.services.league_service import LeagueService

router = APIRouter()


@router.get("/")
async def get_leagues(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    session: AsyncSession = Depends(get_postgres_session)
):
    """
    Get all leagues
    """
    result = await session.execute(
        select(League)
        .where(League.is_active == True)
        .order_by(League.priority.desc(), League.name)
        .offset(skip)
        .limit(limit)
    )
    leagues = result.scalars().all()

    return [
        {
            "id": str(league.id),
            "name": league.name,
            "country": league.country,
            "logo_url": league.logo_url,
            "season": league.season
        }
        for league in leagues
    ]


@router.get("/{league_id}")
async def get_league(
    league_id: UUID,
    session: AsyncSession = Depends(get_postgres_session)
):
    """
    Get league details
    """
    result = await session.execute(
        select(League).where(League.id == league_id)
    )
    league = result.scalar_one_or_none()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )

    return {
        "id": str(league.id),
        "name": league.name,
        "country": league.country,
        "logo_url": league.logo_url,
        "season": league.season
    }


@router.get("/{league_id}/table")
async def get_league_table(
    league_id: UUID,
    session: AsyncSession = Depends(get_postgres_session),
    db = Depends(get_mongo_db)
):
    """
    Get league standings/table
    """
    # Verify league exists
    result = await session.execute(
        select(League).where(League.id == league_id)
    )
    league = result.scalar_one_or_none()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )

    # Get standings from MongoDB
    service = LeagueService(db)
    table = await service.get_league_table(str(league_id), league.season)

    if not table:
        return {
            "league_id": str(league_id),
            "season": league.season,
            "standings": []
        }

    return table


@router.get("/{league_id}/fixtures")
async def get_league_fixtures(
    league_id: UUID,
    limit: int = Query(50, le=100),
    session: AsyncSession = Depends(get_postgres_session),
    db = Depends(get_mongo_db)
):
    """
    Get league fixtures
    """
    # Verify league exists
    result = await session.execute(
        select(League).where(League.id == league_id)
    )
    league = result.scalar_one_or_none()

    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League not found"
        )

    # Get fixtures from MongoDB
    service = LeagueService(db)
    fixtures = await service.get_league_fixtures(str(league_id), limit=limit)

    return fixtures
