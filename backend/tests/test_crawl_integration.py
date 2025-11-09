"""
End-to-end integration tests for crawler-to-database flow

This test suite validates:
- Data validation and transformation
- Duplicate detection
- Upsert functionality
- Event merging
- Error handling
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from typing import Dict, Any

# Import modules to test
from api.services.match_service import MatchService
from crawlers.validators import (
    validate_crawled_data,
    transform_for_database,
    CrawledMatchData,
    CrawledEvent,
    CrawledScore,
    CrawlDataTransformer
)


# Test MongoDB connection
TEST_MONGO_URI = os.getenv('TEST_MONGO_URI', 'mongodb://admin:password123@localhost:27017')
TEST_DB_NAME = 'football_live_test'


@pytest.fixture
async def mongo_client():
    """Create test MongoDB client"""
    client = AsyncIOMotorClient(TEST_MONGO_URI)
    yield client
    client.close()


@pytest.fixture
async def test_db(mongo_client):
    """Create test database and clean it after test"""
    db = mongo_client[TEST_DB_NAME]

    # Clean database before test
    await db.matches.delete_many({})

    yield db

    # Clean database after test
    await db.matches.delete_many({})


@pytest.fixture
async def match_service(test_db):
    """Create MatchService instance"""
    return MatchService(test_db)


# Test Data
def get_sample_crawled_data() -> Dict[str, Any]:
    """Get sample crawled match data"""
    return {
        'score': {'home': 2, 'away': 1},
        'minute': 67,
        'status': 'live',
        'events': [
            {
                'type': 'goal',
                'minute': 23,
                'player': 'John Doe',
                'team': 'home',
                'assist': 'Jane Smith'
            },
            {
                'type': 'yellow_card',
                'minute': 45,
                'player': 'Bob Wilson',
                'team': 'away'
            }
        ],
        'statistics': {
            'possession': {'home': 55, 'away': 45},
            'shots': {'home': 12, 'away': 8},
            'shots_on_target': {'home': 6, 'away': 3}
        }
    }


def get_sample_match_doc() -> Dict[str, Any]:
    """Get sample match document for database"""
    return {
        'external_id': 'test_match_001',
        'home_team': {
            'name': 'Home Team FC',
            'short_name': 'HOME'
        },
        'away_team': {
            'name': 'Away United',
            'short_name': 'AWAY'
        },
        'league': {
            'name': 'Test League',
            'country': 'Test Country'
        },
        'match_date': datetime.utcnow(),
        'status': 'live',
        'score': {'home': 1, 'away': 0},
        'events': [],
        'created_at': datetime.utcnow(),
        'updated_at': datetime.utcnow()
    }


class TestDataValidation:
    """Test data validation layer"""

    def test_validate_valid_data(self):
        """Test validation with valid data"""
        data = get_sample_crawled_data()
        validated = validate_crawled_data(data)

        assert validated is not None
        assert validated.score.home == 2
        assert validated.score.away == 1
        assert validated.status == 'live'
        assert len(validated.events) == 2

    def test_validate_invalid_score(self):
        """Test validation with invalid score"""
        data = get_sample_crawled_data()
        data['score'] = {'home': -1, 'away': 200}  # Invalid values

        validated = validate_crawled_data(data)
        assert validated is None  # Should fail validation

    def test_validate_status_normalization(self):
        """Test status normalization"""
        test_cases = [
            ('FT', 'finished'),
            ('Live', 'live'),
            ('HT', 'halftime'),
            ('Not Started', 'scheduled')
        ]

        for raw_status, expected in test_cases:
            data = get_sample_crawled_data()
            data['status'] = raw_status
            validated = validate_crawled_data(data)

            assert validated is not None
            assert validated.status == expected

    def test_validate_events_sorting(self):
        """Test that events are sorted by minute"""
        data = get_sample_crawled_data()
        # Add events out of order
        data['events'] = [
            {'type': 'goal', 'minute': 67, 'player': 'Player 3', 'team': 'home'},
            {'type': 'goal', 'minute': 23, 'player': 'Player 1', 'team': 'home'},
            {'type': 'yellow_card', 'minute': 45, 'player': 'Player 2', 'team': 'away'}
        ]

        validated = validate_crawled_data(data)
        assert validated is not None

        minutes = [e.minute for e in validated.events]
        assert minutes == sorted(minutes)  # Should be in order


class TestDataTransformation:
    """Test data transformation layer"""

    def test_transform_basic_data(self):
        """Test basic data transformation"""
        raw_data = get_sample_crawled_data()
        transformed = transform_for_database(raw_data)

        assert transformed is not None
        assert 'score' in transformed
        assert 'status' in transformed
        assert 'updated_at' in transformed
        assert transformed['score']['home'] == 2
        assert transformed['score']['away'] == 1

    def test_transform_with_existing_match(self):
        """Test transformation with existing match data"""
        raw_data = get_sample_crawled_data()
        existing_match = get_sample_match_doc()

        transformed = transform_for_database(raw_data, existing_match)

        assert transformed is not None
        assert 'events' in transformed

    def test_event_merging(self):
        """Test event merging logic"""
        existing_events = [
            {'type': 'goal', 'minute': 10, 'player': 'Player A', 'team': 'home'}
        ]

        new_events = [
            {'type': 'goal', 'minute': 10, 'player': 'Player A', 'team': 'home'},  # Duplicate
            {'type': 'goal', 'minute': 20, 'player': 'Player B', 'team': 'away'}   # New
        ]

        merged = CrawlDataTransformer._merge_events(existing_events, new_events)

        assert len(merged) == 2  # Should have 2 unique events
        assert merged[0]['minute'] == 10
        assert merged[1]['minute'] == 20


@pytest.mark.asyncio
class TestMatchServiceIntegration:
    """Test MatchService integration with crawler data"""

    async def test_upsert_new_match(self, match_service):
        """Test upserting a new match"""
        match_data = get_sample_match_doc()
        external_id = 'test_match_new'

        result, is_new = await match_service.upsert_match(external_id, match_data)

        assert is_new is True
        assert result['external_id'] == external_id
        assert result['status'] == 'live'

    async def test_upsert_existing_match(self, match_service):
        """Test upserting an existing match"""
        external_id = 'test_match_existing'

        # Create initial match
        initial_data = get_sample_match_doc()
        await match_service.upsert_match(external_id, initial_data)

        # Update the match
        update_data = get_sample_match_doc()
        update_data['score'] = {'home': 3, 'away': 1}
        update_data['status'] = 'finished'

        result, is_new = await match_service.upsert_match(external_id, update_data)

        assert is_new is False
        assert result['score']['home'] == 3
        assert result['status'] == 'finished'

    async def test_duplicate_detection(self, match_service):
        """Test duplicate match detection"""
        match_date = datetime.utcnow()

        # Create a match
        match_data = get_sample_match_doc()
        match_data['match_date'] = match_date
        await match_service.create_match(match_data)

        # Try to find duplicate
        duplicate = await match_service.detect_duplicate_match(
            home_team='Home Team FC',
            away_team='Away United',
            match_date=match_date,
            tolerance_hours=3
        )

        assert duplicate is not None
        assert duplicate['home_team']['name'] == 'Home Team FC'

    async def test_get_matches_requiring_updates(self, match_service):
        """Test getting matches that need updates"""
        # Create live match
        live_match = get_sample_match_doc()
        live_match['external_id'] = 'live_match'
        live_match['status'] = 'live'
        await match_service.create_match(live_match)

        # Create scheduled match today
        scheduled_match = get_sample_match_doc()
        scheduled_match['external_id'] = 'scheduled_match'
        scheduled_match['status'] = 'scheduled'
        scheduled_match['match_date'] = datetime.utcnow()
        await match_service.create_match(scheduled_match)

        # Create finished match (should not be included)
        finished_match = get_sample_match_doc()
        finished_match['external_id'] = 'finished_match'
        finished_match['status'] = 'finished'
        await match_service.create_match(finished_match)

        # Get matches requiring updates
        matches = await match_service.get_matches_requiring_updates()

        assert len(matches) >= 2  # At least live and scheduled
        statuses = [m['status'] for m in matches]
        assert 'live' in statuses
        assert 'scheduled' in statuses
        assert 'finished' not in statuses


@pytest.mark.asyncio
class TestEndToEndCrawlFlow:
    """Test complete end-to-end crawl flow"""

    async def test_complete_crawl_flow(self, match_service):
        """
        Test complete flow:
        1. Crawler returns raw data
        2. Data is validated
        3. Data is transformed
        4. Match is upserted to database
        5. Events are properly merged
        """
        external_id = 'e2e_test_match'

        # Step 1: Create initial match in database
        initial_match = get_sample_match_doc()
        initial_match['external_id'] = external_id
        initial_match['status'] = 'live'
        initial_match['score'] = {'home': 1, 'away': 0}
        initial_match['events'] = [
            {'type': 'goal', 'minute': 10, 'player': 'Early Scorer', 'team': 'home'}
        ]
        await match_service.create_match(initial_match)

        # Step 2: Simulate crawler returning updated data
        raw_crawled_data = {
            'score': {'home': 2, 'away': 1},
            'minute': 75,
            'status': 'live',
            'events': [
                # Duplicate event (should not be added again)
                {'type': 'goal', 'minute': 10, 'player': 'Early Scorer', 'team': 'home'},
                # New events
                {'type': 'goal', 'minute': 67, 'player': 'Late Scorer', 'team': 'home'},
                {'type': 'goal', 'minute': 70, 'player': 'Opposition', 'team': 'away'}
            ],
            'statistics': {
                'possession': {'home': 60, 'away': 40},
                'shots': {'home': 15, 'away': 10}
            }
        }

        # Step 3: Validate data
        validated = validate_crawled_data(raw_crawled_data)
        assert validated is not None

        # Step 4: Get existing match and transform data
        existing = await match_service.get_match_by_external_id(external_id)
        transformed = transform_for_database(raw_crawled_data, existing)
        assert transformed is not None

        # Step 5: Upsert to database
        updated_match, is_new = await match_service.upsert_match(external_id, transformed)

        # Verify results
        assert is_new is False  # Should update existing
        assert updated_match['score']['home'] == 2
        assert updated_match['score']['away'] == 1
        assert updated_match['minute'] == 75

        # Verify events were merged correctly (3 unique events)
        assert len(updated_match['events']) == 3

        event_signatures = {
            f"{e['type']}_{e['minute']}_{e['player']}"
            for e in updated_match['events']
        }
        assert len(event_signatures) == 3  # All unique

        print("\n✓ End-to-end crawl flow test passed!")
        print(f"  Match updated: {external_id}")
        print(f"  Final score: {updated_match['score']['home']}-{updated_match['score']['away']}")
        print(f"  Total events: {len(updated_match['events'])}")
        print(f"  Status: {updated_match['status']}")


# Script to run tests manually
if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("CRAWL INTEGRATION TEST SUITE")
    print("=" * 60)

    # Run with pytest
    exit_code = pytest.main([__file__, '-v', '-s'])

    sys.exit(exit_code)
