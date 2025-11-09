# 🔄 Crawl-to-Database Integration

> Complete documentation for the crawler-to-database integration system

Last Updated: 2024-11-09

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Flow](#data-flow)
4. [Components](#components)
5. [Usage Guide](#usage-guide)
6. [Testing](#testing)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The crawl-to-database integration implements a robust pipeline for:

- ✅ **Data Validation** - Validate and sanitize crawled data using Pydantic models
- ✅ **Data Transformation** - Transform crawler format to database schema
- ✅ **Duplicate Detection** - Prevent duplicate matches and events
- ✅ **Upsert Operations** - Insert new or update existing matches
- ✅ **Event Merging** - Intelligently merge new events with existing
- ✅ **Error Handling** - Graceful handling of validation and crawl errors
- ✅ **Monitoring & Metrics** - Track crawl performance and health

---

## Architecture

```
┌─────────────────┐
│  Celery Tasks   │
│  (Scheduled)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FlashScore     │◄─── User-Agent Rotation
│  Crawler        │      Rate Limiting
└────────┬────────┘      Retry Logic
         │
         │ Raw Data
         ▼
┌─────────────────┐
│  Validators     │◄─── Pydantic Models
│  (validators.py)│      Data Sanitization
└────────┬────────┘      Status Normalization
         │
         │ Validated Data
         ▼
┌─────────────────┐
│  Transformer    │◄─── Event Merging
│  (validators.py)│      Score Tracking
└────────┬────────┘      Halftime/Fulltime
         │
         │ Transformed Data
         ▼
┌─────────────────┐
│  MatchService   │◄─── Duplicate Detection
│  (upsert)       │      Conflict Resolution
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   MongoDB       │
│  (Matches)      │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Redis Pub/Sub  │◄─── WebSocket Broadcasting
│  (Real-time)    │      Client Updates
└─────────────────┘
```

---

## Data Flow

### 1. Crawl Initiation

**Celery Beat** schedules periodic tasks:
- Live scores: Every 30 seconds
- Match events: Every 10 seconds
- Daily fixtures: Daily at 2 AM

### 2. Data Crawling

**FlashScoreCrawler** fetches data:
```python
raw_data = await crawler.crawl_match(external_id)
# Returns: {
#   'score': {'home': 2, 'away': 1},
#   'minute': 67,
#   'status': 'live',
#   'events': [...],
#   'statistics': {...}
# }
```

### 3. Validation

**validators.py** validates data:
```python
from crawlers.validators import validate_crawled_data

validated = validate_crawled_data(raw_data)
# Returns: CrawledMatchData or None
```

Validation includes:
- Score range checks (0-99)
- Status normalization ('FT' → 'finished')
- Event type validation
- Player name sanitization
- Statistics structure validation

### 4. Transformation

**CrawlDataTransformer** transforms data:
```python
from crawlers.validators import transform_for_database

transformed = transform_for_database(raw_data, existing_match)
# Returns: Database-ready dictionary
```

Transformation handles:
- Event deduplication
- Halftime/fulltime score tracking
- Timestamp updates
- Event sorting by minute

### 5. Database Upsert

**MatchService** upserts to MongoDB:
```python
updated_match, is_new = await service.upsert_match(
    external_id='flashscore_12345',
    match_data=transformed
)
```

Upsert logic:
- If `external_id` exists → UPDATE
- If `external_id` not found → INSERT
- Returns `(match, is_new_flag)`

### 6. Real-time Broadcasting

**Redis Pub/Sub** broadcasts updates:
```python
await publish_match_update(match_id, data)
```

WebSocket clients receive:
```json
{
  "type": "match_update",
  "channel": "match:12345",
  "data": {
    "match_id": "12345",
    "score": {"home": 2, "away": 1},
    "minute": 67,
    "status": "live"
  }
}
```

---

## Components

### 1. Data Validators (`backend/crawlers/validators.py`)

#### CrawledScore
```python
class CrawledScore(BaseModel):
    home: int = Field(ge=0, le=99)
    away: int = Field(ge=0, le=99)
```

#### CrawledEvent
```python
class CrawledEvent(BaseModel):
    type: str  # goal, yellow_card, red_card, substitution
    minute: int = Field(ge=0, le=200)
    player: str
    team: str  # home or away
    assist: Optional[str] = None
```

#### CrawledMatchData
```python
class CrawledMatchData(BaseModel):
    score: CrawledScore
    minute: Optional[int]
    status: str  # scheduled, live, halftime, finished
    events: List[CrawledEvent] = []
    statistics: Optional[CrawledStatistics] = None
```

### 2. Data Transformer (`backend/crawlers/validators.py`)

#### CrawlDataTransformer

**Key Methods:**

- `transform_match_data()` - Transform crawler data to DB format
- `_merge_events()` - Merge events avoiding duplicates

**Event Deduplication:**
```python
signature = f"{event['type']}_{event['minute']}_{event['player']}_{event['team']}"
```

### 3. MatchService Extensions (`backend/api/services/match_service.py`)

#### New Methods

**upsert_match(external_id, match_data)**
- Insert or update based on external_id
- Returns (match, is_new)

**detect_duplicate_match(home_team, away_team, match_date)**
- Detect duplicates by teams + date ± tolerance
- Returns existing match or None

**get_matches_requiring_updates(limit)**
- Get live + today's scheduled matches
- For crawl prioritization

### 4. Enhanced Celery Tasks

#### live_scores.py

**crawl_live_scores()**
- Crawls matches requiring updates
- Validates and transforms data
- Upserts to database
- Broadcasts updates via Redis

**crawl_match_events()**
- Crawls events for live matches
- Validates events
- Detects new events
- Publishes to Redis

#### fixtures.py

**crawl_daily_fixtures()**
- Crawls upcoming fixtures
- Validates data
- Detects duplicates
- Stores in database

### 5. Monitoring System (`backend/crawlers/monitoring.py`)

#### CrawlMetrics

Tracks:
- Total crawls
- Success/failure rates
- Validation error rates
- Duplicate detection stats
- Average crawl duration

```python
from crawlers.monitoring import crawl_metrics

metrics = crawl_metrics.get_metrics('crawl_live_scores')
# Returns: {
#   'total': 100,
#   'success': 95,
#   'failed': 5,
#   'success_rate': 95.0,
#   'avg_duration': 2.3,
#   ...
# }
```

#### CrawlJobMonitor

Logs job execution to MongoDB:
```python
monitor = CrawlJobMonitor(db)

# Log start
job_id = await monitor.log_job_start(
    task_name='crawl_live_scores',
    task_id=celery_task_id,
    params={}
)

# Log completion
await monitor.log_job_complete(
    task_id=celery_task_id,
    result={'matches_updated': 10},
    error=None
)
```

---

## Usage Guide

### Running Crawl Tasks

#### 1. Start Celery Worker

```bash
cd backend
celery -A tasks.celery_app worker --loglevel=info
```

#### 2. Start Celery Beat (Scheduler)

```bash
celery -A tasks.celery_app beat --loglevel=info
```

#### 3. Monitor Tasks

```bash
# View active tasks
celery -A tasks.celery_app inspect active

# View scheduled tasks
celery -A tasks.celery_app inspect scheduled

# View registered tasks
celery -A tasks.celery_app inspect registered
```

### Manual Task Execution

```python
from tasks.live_scores import crawl_live_scores

# Execute immediately
result = crawl_live_scores.delay()

# Check result
print(result.get())
# {'matches_updated': 5, 'matches_created': 2, 'validation_failures': 1}
```

### Checking Health

```python
from crawlers.monitoring import get_crawler_health

health = await get_crawler_health()
print(health)
# {
#   'status': 'healthy',
#   'message': 'All systems operating normally.',
#   'total_crawls': 150,
#   'overall_failure_rate': 3.2,
#   ...
# }
```

---

## Testing

### Running Integration Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
cd backend
pytest tests/test_crawl_integration.py -v

# Run specific test
pytest tests/test_crawl_integration.py::TestEndToEndCrawlFlow::test_complete_crawl_flow -v
```

### Test Coverage

Tests validate:
- ✅ Data validation with valid/invalid data
- ✅ Status normalization
- ✅ Event sorting
- ✅ Data transformation
- ✅ Event merging logic
- ✅ Upsert operations (new + existing)
- ✅ Duplicate detection
- ✅ End-to-end crawl flow

### Manual Testing

```python
# Test validation
from crawlers.validators import validate_crawled_data

data = {
    'score': {'home': 2, 'away': 1},
    'status': 'FT',  # Will normalize to 'finished'
    'minute': 90,
    'events': [],
    'statistics': None
}

validated = validate_crawled_data(data)
print(validated.status)  # 'finished'
```

---

## Monitoring

### Health Checks

```python
from crawlers.monitoring import get_crawler_health, print_crawler_metrics

# Get health status
health = await get_crawler_health()

# Print detailed metrics
await print_crawler_metrics()
```

### Metrics Dashboard

View metrics:
```python
from crawlers.monitoring import crawl_metrics

# All metrics
all_metrics = crawl_metrics.get_metrics()

# Specific task
task_metrics = crawl_metrics.get_metrics('crawl_live_scores')
```

### Job History

```python
from crawlers.monitoring import CrawlJobMonitor

monitor = CrawlJobMonitor(db)

# Recent jobs
jobs = await monitor.get_recent_jobs(limit=20)

# Statistics
stats = await monitor.get_job_statistics(hours=24)
```

### Logs

Structured logging with `structlog`:

```python
import structlog
logger = structlog.get_logger()

# Logs include context
logger.info(
    "match_crawl_success",
    match_id=match_id,
    external_id=external_id,
    status=status,
    is_new=is_new
)
```

Log format (JSON):
```json
{
  "event": "match_crawl_success",
  "match_id": "507f1f77bcf86cd799439011",
  "external_id": "flashscore_12345",
  "status": "live",
  "is_new": false,
  "timestamp": "2024-11-09T10:30:45Z"
}
```

---

## Troubleshooting

### Common Issues

#### 1. High Validation Error Rate

**Symptoms:**
- Many `validation_error` logs
- Low `success_rate` in metrics

**Causes:**
- Crawler selectors outdated
- Website structure changed
- Invalid data format

**Solutions:**
```bash
# Check recent validation errors
grep "data_validation_failed" celery.log | tail -20

# Update crawler selectors
# Edit: backend/crawlers/flashscore.py
```

#### 2. Duplicate Events

**Symptoms:**
- Same event appearing multiple times
- Event count increasing on each crawl

**Causes:**
- Event signature not unique enough
- Player name variations

**Solutions:**
```python
# Event signature includes:
# type + minute + player + team

# Ensure player names are normalized
# in CrawledEvent.clean_player_name()
```

#### 3. Matches Not Updating

**Symptoms:**
- Live matches stuck with old data
- No `match_updated` logs

**Causes:**
- Crawler returning no data
- external_id mismatch
- Database connection issues

**Solutions:**
```python
# Check crawler output
logger.debug("raw_crawler_data", data=raw_data)

# Verify external_id consistency
# Check: match.external_id matches crawler ID

# Test database connection
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient(MONGO_URI)
await client.admin.command('ping')
```

#### 4. Celery Tasks Not Running

**Symptoms:**
- No task logs
- Beat schedule not executing

**Solutions:**
```bash
# Check Celery worker is running
ps aux | grep celery

# Check Celery beat is running
ps aux | grep "celery beat"

# View beat schedule
celery -A tasks.celery_app inspect scheduled

# Restart services
pkill -f celery
celery -A tasks.celery_app worker -l info &
celery -A tasks.celery_app beat -l info &
```

---

## Performance Optimization

### Best Practices

1. **Batch Processing**
   - Process matches in batches
   - Use `asyncio.gather()` for parallel crawls

2. **Rate Limiting**
   - Respect website rate limits
   - Use exponential backoff on errors

3. **Caching**
   - Cache team/league data
   - Reduce database queries

4. **Database Indexes**
   ```javascript
   // MongoDB indexes
   db.matches.createIndex({ "external_id": 1 }, { unique: true })
   db.matches.createIndex({ "status": 1, "match_date": 1 })
   db.matches.createIndex({ "home_team.name": 1, "away_team.name": 1, "match_date": 1 })
   ```

5. **Selective Crawling**
   - Prioritize live matches
   - Reduce frequency for finished matches

---

## Next Steps

After implementing crawl-to-DB integration, proceed with:

1. **Real-time Notifications** (Day 24-25)
   - Redis Pub/Sub implementation
   - WebSocket broadcasting
   - Client subscription management

2. **Production Crawler** (Week 5+)
   - Update FlashScore selectors with real HTML
   - Implement proxy rotation
   - Add Cloudflare bypass

3. **Advanced Monitoring** (Week 9+)
   - Prometheus metrics
   - Grafana dashboards
   - Alert system

---

## Summary

The crawl-to-database integration provides:

✅ **Robust Data Pipeline** - From crawler to database
✅ **Data Quality** - Validation and sanitization
✅ **Duplicate Prevention** - Smart detection logic
✅ **Error Handling** - Graceful failure recovery
✅ **Monitoring** - Comprehensive metrics and logs
✅ **Testing** - Full test coverage

**Status**: ✅ COMPLETE

---

*For questions or issues, check logs and metrics first, then refer to troubleshooting section.*
