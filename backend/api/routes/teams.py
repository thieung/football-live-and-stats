"""
Teams routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from api.core.database import get_postgres_session, get_mongo_db
from api.models.postgres import Team

router = APIRouter()


@router.get("/{team_id}")
async def get_team(
    team_id: UUID,
    session: AsyncSession = Depends(get_postgres_session)
):
    """
    Get team details
    """
    result = await session.execute(
        select(Team).where(Team.id == team_id)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    return {
        "id": str(team.id),
        "name": team.name,
        "short_name": team.short_name,
        "logo_url": team.logo_url,
        "country": team.country,
        "stadium": team.stadium
    }


@router.get("/{team_id}/fixtures")
async def get_team_fixtures(
    team_id: UUID,
    limit: int = Query(20, le=50),
    session: AsyncSession = Depends(get_postgres_session),
    db = Depends(get_mongo_db)
):
    """
    Get team fixtures (past and upcoming)
    """
    # Verify team exists
    result = await session.execute(
        select(Team).where(Team.id == team_id)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )

    # Get matches from MongoDB
    matches = await db.matches.find(
        {
            "$or": [
                {"home_team.id": str(team_id)},
                {"away_team.id": str(team_id)}
            ]
        }
    ).sort("match_date", -1).limit(limit).to_list(limit)

    return matches
