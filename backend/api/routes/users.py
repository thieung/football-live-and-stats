"""
Users routes (favorites, preferences)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID
from typing import List
from pydantic import BaseModel

from api.core.database import get_postgres_session
from api.core.security import get_current_user
from api.models.postgres import User, UserFavorite

router = APIRouter()


class FavoriteCreate(BaseModel):
    entity_type: str  # 'team' or 'league'
    entity_id: UUID


@router.get("/favorites")
async def get_favorites(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_postgres_session)
):
    """
    Get user's favorite teams and leagues
    """
    result = await session.execute(
        select(UserFavorite).where(UserFavorite.user_id == current_user.id)
    )
    favorites = result.scalars().all()

    return [
        {
            "id": str(fav.id),
            "entity_type": fav.entity_type,
            "entity_id": str(fav.entity_id)
        }
        for fav in favorites
    ]


@router.post("/favorites", status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_postgres_session)
):
    """
    Add a favorite team or league
    """
    if favorite.entity_type not in ['team', 'league']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="entity_type must be 'team' or 'league'"
        )

    # Check if already exists
    result = await session.execute(
        select(UserFavorite).where(
            UserFavorite.user_id == current_user.id,
            UserFavorite.entity_type == favorite.entity_type,
            UserFavorite.entity_id == favorite.entity_id
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already in favorites"
        )

    # Create new favorite
    new_favorite = UserFavorite(
        user_id=current_user.id,
        entity_type=favorite.entity_type,
        entity_id=favorite.entity_id
    )

    session.add(new_favorite)
    await session.commit()
    await session.refresh(new_favorite)

    return {
        "id": str(new_favorite.id),
        "entity_type": new_favorite.entity_type,
        "entity_id": str(new_favorite.entity_id)
    }


@router.delete("/favorites/{favorite_id}")
async def remove_favorite(
    favorite_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_postgres_session)
):
    """
    Remove a favorite
    """
    result = await session.execute(
        select(UserFavorite).where(
            UserFavorite.id == favorite_id,
            UserFavorite.user_id == current_user.id
        )
    )
    favorite = result.scalar_one_or_none()

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )

    await session.delete(favorite)
    await session.commit()

    return {"message": "Favorite removed"}
