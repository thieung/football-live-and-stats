"""
PostgreSQL database models using SQLAlchemy
"""
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from api.core.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    favorites = relationship("UserFavorite", back_populates="user", cascade="all, delete-orphan")


class League(Base):
    """League model"""
    __tablename__ = "leagues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, index=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100))
    logo_url = Column(String(500))
    season = Column(String(20))  # "2024/2025"
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Display priority
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    fixtures = relationship("Fixture", back_populates="league")


class Team(Base):
    """Team model"""
    __tablename__ = "teams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, index=True)
    name = Column(String(255), nullable=False)
    short_name = Column(String(50))
    logo_url = Column(String(500))
    country = Column(String(100))
    stadium = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    home_fixtures = relationship("Fixture", foreign_keys="Fixture.home_team_id", back_populates="home_team")
    away_fixtures = relationship("Fixture", foreign_keys="Fixture.away_team_id", back_populates="away_team")


class Fixture(Base):
    """Fixture/Match schedule model"""
    __tablename__ = "fixtures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, index=True)
    league_id = Column(UUID(as_uuid=True), ForeignKey("leagues.id"), nullable=False)
    home_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)
    match_date = Column(DateTime(timezone=True), nullable=False, index=True)
    venue = Column(String(255))
    round = Column(String(50))
    status = Column(String(50), default="scheduled", index=True)  # scheduled, live, finished, postponed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    league = relationship("League", back_populates="fixtures")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_fixtures")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_fixtures")

    # Composite index for efficient queries
    __table_args__ = (
        UniqueConstraint('league_id', 'home_team_id', 'away_team_id', 'match_date', name='uix_fixture'),
    )


class UserFavorite(Base):
    """User favorites (teams/leagues)"""
    __tablename__ = "user_favorites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    entity_type = Column(String(20), nullable=False)  # 'team' or 'league'
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="favorites")

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'entity_type', 'entity_id', name='uix_user_favorite'),
    )


class CrawlJob(Base):
    """Crawl job tracking"""
    __tablename__ = "crawl_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_type = Column(String(100), nullable=False)  # 'live_scores', 'fixtures', 'stats'
    source = Column(String(100), nullable=False)  # 'flashscore', 'livescore'
    status = Column(String(50), default="pending", index=True)  # pending, running, success, failed
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    items_crawled = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
