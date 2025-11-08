"""
Seed initial data for testing

This script populates the database with:
- Major football leagues
- Popular teams
- Sample fixtures
- Test matches for development
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from datetime import datetime, timedelta
from sqlalchemy import select
from api.core.database import AsyncSessionLocal, get_mongo_db, mongo_client
from api.models.postgres import League, Team, Fixture
from api.core.config import settings
import structlog

logger = structlog.get_logger()


async def seed_leagues():
    """Seed major football leagues"""
    leagues_data = [
        {
            "external_id": "epl_2024",
            "source": "manual",
            "name": "Premier League",
            "short_name": "EPL",
            "country": "England",
            "country_code": "ENG",
            "season": "2024/2025",
            "is_active": True,
            "is_featured": True,
            "priority": 10,
            "num_teams": 20
        },
        {
            "external_id": "laliga_2024",
            "source": "manual",
            "name": "La Liga",
            "short_name": "La Liga",
            "country": "Spain",
            "country_code": "ESP",
            "season": "2024/2025",
            "is_active": True,
            "is_featured": True,
            "priority": 9,
            "num_teams": 20
        },
        {
            "external_id": "bundesliga_2024",
            "source": "manual",
            "name": "Bundesliga",
            "short_name": "Bundesliga",
            "country": "Germany",
            "country_code": "GER",
            "season": "2024/2025",
            "is_active": True,
            "is_featured": True,
            "priority": 8,
            "num_teams": 18
        },
        {
            "external_id": "seriea_2024",
            "source": "manual",
            "name": "Serie A",
            "short_name": "Serie A",
            "country": "Italy",
            "country_code": "ITA",
            "season": "2024/2025",
            "is_active": True,
            "is_featured": True,
            "priority": 7,
            "num_teams": 20
        },
        {
            "external_id": "ligue1_2024",
            "source": "manual",
            "name": "Ligue 1",
            "short_name": "Ligue 1",
            "country": "France",
            "country_code": "FRA",
            "season": "2024/2025",
            "is_active": True,
            "is_featured": True,
            "priority": 6,
            "num_teams": 18
        }
    ]

    async with AsyncSessionLocal() as session:
        created_leagues = []
        for league_data in leagues_data:
            # Check if exists
            result = await session.execute(
                select(League).where(League.external_id == league_data["external_id"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.info("league_exists", name=league_data["name"])
                created_leagues.append(existing)
                continue

            league = League(**league_data)
            session.add(league)
            created_leagues.append(league)
            logger.info("league_created", name=league_data["name"])

        await session.commit()

        # Refresh to get IDs
        for league in created_leagues:
            await session.refresh(league)

        return created_leagues


async def seed_teams():
    """Seed popular football teams"""
    teams_data = [
        # Premier League
        {"external_id": "man_utd", "name": "Manchester United", "short_name": "Man United", "acronym": "MUN", "country": "England"},
        {"external_id": "liverpool", "name": "Liverpool", "short_name": "Liverpool", "acronym": "LIV", "country": "England"},
        {"external_id": "man_city", "name": "Manchester City", "short_name": "Man City", "acronym": "MCI", "country": "England"},
        {"external_id": "chelsea", "name": "Chelsea", "short_name": "Chelsea", "acronym": "CHE", "country": "England"},
        {"external_id": "arsenal", "name": "Arsenal", "short_name": "Arsenal", "acronym": "ARS", "country": "England"},
        {"external_id": "tottenham", "name": "Tottenham Hotspur", "short_name": "Tottenham", "acronym": "TOT", "country": "England"},

        # La Liga
        {"external_id": "real_madrid", "name": "Real Madrid", "short_name": "Real Madrid", "acronym": "RMA", "country": "Spain"},
        {"external_id": "barcelona", "name": "Barcelona", "short_name": "Barcelona", "acronym": "BAR", "country": "Spain"},
        {"external_id": "atletico", "name": "Atletico Madrid", "short_name": "Atletico", "acronym": "ATM", "country": "Spain"},

        # Bundesliga
        {"external_id": "bayern", "name": "Bayern Munich", "short_name": "Bayern", "acronym": "BAY", "country": "Germany"},
        {"external_id": "dortmund", "name": "Borussia Dortmund", "short_name": "Dortmund", "acronym": "BVB", "country": "Germany"},

        # Serie A
        {"external_id": "juventus", "name": "Juventus", "short_name": "Juventus", "acronym": "JUV", "country": "Italy"},
        {"external_id": "inter", "name": "Inter Milan", "short_name": "Inter", "acronym": "INT", "country": "Italy"},
        {"external_id": "milan", "name": "AC Milan", "short_name": "Milan", "acronym": "MIL", "country": "Italy"},

        # Ligue 1
        {"external_id": "psg", "name": "Paris Saint-Germain", "short_name": "PSG", "acronym": "PSG", "country": "France"},
    ]

    async with AsyncSessionLocal() as session:
        created_teams = []
        for team_data in teams_data:
            # Check if exists
            result = await session.execute(
                select(Team).where(Team.external_id == team_data["external_id"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.info("team_exists", name=team_data["name"])
                created_teams.append(existing)
                continue

            team = Team(source="manual", **team_data)
            session.add(team)
            created_teams.append(team)
            logger.info("team_created", name=team_data["name"])

        await session.commit()

        # Refresh to get IDs
        for team in created_teams:
            await session.refresh(team)

        return created_teams


async def seed_fixtures(leagues, teams):
    """Seed sample fixtures"""
    # Get EPL teams
    epl = next(l for l in leagues if l.short_name == "EPL")

    man_utd = next(t for t in teams if t.acronym == "MUN")
    liverpool = next(t for t in teams if t.acronym == "LIV")
    man_city = next(t for t in teams if t.acronym == "MCI")
    chelsea = next(t for t in teams if t.acronym == "CHE")
    arsenal = next(t for t in teams if t.acronym == "ARS")

    now = datetime.utcnow()

    fixtures_data = [
        {
            "external_id": "fixture_1",
            "league_id": epl.id,
            "home_team_id": man_utd.id,
            "away_team_id": liverpool.id,
            "match_date": now - timedelta(hours=2),  # Finished match
            "status": "finished",
            "round": "Matchday 11"
        },
        {
            "external_id": "fixture_2",
            "league_id": epl.id,
            "home_team_id": man_city.id,
            "away_team_id": chelsea.id,
            "match_date": now + timedelta(minutes=30),  # Live soon
            "status": "live",
            "round": "Matchday 11"
        },
        {
            "external_id": "fixture_3",
            "league_id": epl.id,
            "home_team_id": arsenal.id,
            "away_team_id": man_utd.id,
            "match_date": now + timedelta(hours=3),  # Upcoming
            "status": "scheduled",
            "round": "Matchday 11"
        }
    ]

    async with AsyncSessionLocal() as session:
        created_fixtures = []
        for fixture_data in fixtures_data:
            # Check if exists
            result = await session.execute(
                select(Fixture).where(Fixture.external_id == fixture_data["external_id"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                logger.info("fixture_exists", external_id=fixture_data["external_id"])
                created_fixtures.append(existing)
                continue

            fixture = Fixture(source="manual", **fixture_data)
            session.add(fixture)
            created_fixtures.append(fixture)
            logger.info("fixture_created", external_id=fixture_data["external_id"])

        await session.commit()

        # Refresh to get IDs
        for fixture in created_fixtures:
            await session.refresh(fixture)

        return created_fixtures


async def seed_matches(fixtures, leagues, teams):
    """Seed sample matches in MongoDB"""
    # Initialize MongoDB
    db = mongo_client[settings.MONGO_DB_NAME]

    # Get references
    epl = next(l for l in leagues if l.short_name == "EPL")
    man_utd = next(t for t in teams if t.acronym == "MUN")
    liverpool = next(t for t in teams if t.acronym == "LIV")
    man_city = next(t for t in teams if t.acronym == "MCI")
    chelsea = next(t for t in teams if t.acronym == "CHE")

    now = datetime.utcnow()

    matches_data = [
        {
            "external_id": "match_1",
            "source": "manual",
            "fixture_id": str(fixtures[0].id),
            "league": {
                "id": str(epl.id),
                "name": epl.name,
                "country": epl.country,
            },
            "home_team": {
                "id": str(man_utd.id),
                "name": man_utd.name,
                "short_name": man_utd.short_name,
            },
            "away_team": {
                "id": str(liverpool.id),
                "name": liverpool.name,
                "short_name": liverpool.short_name,
            },
            "match_date": now - timedelta(hours=2),
            "status": "finished",
            "score": {
                "home": 2,
                "away": 1,
                "halftime": {"home": 1, "away": 0},
                "fulltime": {"home": 2, "away": 1}
            },
            "events": [
                {
                    "type": "goal",
                    "minute": 23,
                    "player": "Marcus Rashford",
                    "team": "home"
                },
                {
                    "type": "goal",
                    "minute": 45,
                    "player": "Bruno Fernandes",
                    "team": "home"
                },
                {
                    "type": "goal",
                    "minute": 67,
                    "player": "Mohamed Salah",
                    "team": "away"
                }
            ],
            "statistics": {
                "possession": {"home": 55, "away": 45},
                "shots": {"home": 12, "away": 8},
                "shots_on_target": {"home": 5, "away": 3}
            },
            "created_at": now - timedelta(hours=3),
            "updated_at": now
        },
        {
            "external_id": "match_2",
            "source": "manual",
            "fixture_id": str(fixtures[1].id),
            "league": {
                "id": str(epl.id),
                "name": epl.name,
                "country": epl.country,
            },
            "home_team": {
                "id": str(man_city.id),
                "name": man_city.name,
                "short_name": man_city.short_name,
            },
            "away_team": {
                "id": str(chelsea.id),
                "name": chelsea.name,
                "short_name": chelsea.short_name,
            },
            "match_date": now + timedelta(minutes=30),
            "status": "live",
            "minute": 35,
            "score": {
                "home": 1,
                "away": 0,
                "halftime": None
            },
            "events": [
                {
                    "type": "goal",
                    "minute": 15,
                    "player": "Erling Haaland",
                    "team": "home"
                }
            ],
            "statistics": {
                "possession": {"home": 60, "away": 40},
                "shots": {"home": 8, "away": 4}
            },
            "created_at": now,
            "updated_at": now
        }
    ]

    for match_data in matches_data:
        # Check if exists
        existing = await db.matches.find_one({"external_id": match_data["external_id"]})

        if existing:
            logger.info("match_exists", external_id=match_data["external_id"])
            continue

        result = await db.matches.insert_one(match_data)
        logger.info("match_created", external_id=match_data["external_id"], id=str(result.inserted_id))


async def main():
    """Run all seed functions"""
    logger.info("seeding_started")

    try:
        # Seed in order
        logger.info("seeding_leagues")
        leagues = await seed_leagues()
        logger.info("leagues_seeded", count=len(leagues))

        logger.info("seeding_teams")
        teams = await seed_teams()
        logger.info("teams_seeded", count=len(teams))

        logger.info("seeding_fixtures")
        fixtures = await seed_fixtures(leagues, teams)
        logger.info("fixtures_seeded", count=len(fixtures))

        logger.info("seeding_matches")
        await seed_matches(fixtures, leagues, teams)
        logger.info("matches_seeded")

        logger.info("seeding_completed", status="success")

    except Exception as e:
        logger.error("seeding_failed", error=str(e), exc_info=True)
        raise

    finally:
        # Close MongoDB connection
        mongo_client.close()


if __name__ == "__main__":
    asyncio.run(main())
