# 🗄️ Database Setup Guide

Complete guide for setting up and managing databases for the Football Live Score application.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Database Architecture](#database-architecture)
- [Quick Start](#quick-start)
- [Step-by-Step Setup](#step-by-step-setup)
- [Running Migrations](#running-migrations)
- [Seeding Data](#seeding-data)
- [Testing the Setup](#testing-the-setup)
- [Troubleshooting](#troubleshooting)
- [Production Considerations](#production-considerations)

---

## Prerequisites

### Required Software

- **Docker & Docker Compose** (recommended) OR:
  - PostgreSQL 15+
  - MongoDB 7+
  - Redis 7+
- **Python 3.11+**
- **Git**

### Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

## Database Architecture

The application uses a hybrid database approach:

```
┌─────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                  │
└──────────────┬──────────────────────┬───────────────┘
               │                      │
       ┌───────▼────────┐    ┌────────▼─────────┐
       │  PostgreSQL    │    │    MongoDB       │
       │  (Relational)  │    │   (Document)     │
       └────────────────┘    └──────────────────┘
       │                     │
       │ - Users             │ - Matches (live data)
       │ - Leagues           │ - Match Events
       │ - Teams             │ - Statistics
       │ - Fixtures          │ - Real-time updates
       │ - User Favorites    │
       │ - Crawl Jobs        │
       └─────────────────────┘

               ┌────────────────┐
               │     Redis      │
               │  (Cache/Queue) │
               └────────────────┘
               │
               │ - Session cache
               │ - API cache
               │ - Celery broker
               │ - Pub/Sub for WebSocket
               └─────────────────────
```

### Why Hybrid?

- **PostgreSQL**: Structured, relational data with ACID compliance
- **MongoDB**: Flexible schema for rapidly changing match data
- **Redis**: Fast caching and real-time message brokering

---

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Navigate to backend directory
cd backend

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker compose up -d postgres mongodb redis

# 4. Wait for services to be healthy (30-60 seconds)
docker compose ps

# 5. Run migrations
alembic upgrade head

# 6. Seed initial data
python scripts/seed_data.py

# 7. Verify setup
python scripts/test_setup.py
```

### Option 2: Manual Setup

See [Step-by-Step Setup](#step-by-step-setup) below.

---

## Step-by-Step Setup

### 1. Configure Environment Variables

```bash
cd backend
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database - PostgreSQL
DATABASE_URL=postgresql+asyncpg://admin:password123@localhost:5432/football_db

# Database - MongoDB
MONGO_URI=mongodb://admin:password123@localhost:27017
MONGO_DB_NAME=football_live

# Redis
REDIS_URL=redis://localhost:6379/0
```

### 2. Start Database Services

#### Using Docker Compose

```bash
docker compose up -d postgres mongodb redis
```

**Verify services are running:**

```bash
docker compose ps

# Should show:
# football_postgres    healthy
# football_mongodb     healthy
# football_redis       healthy
```

#### Manual Installation

**PostgreSQL:**
```bash
# Install PostgreSQL
sudo apt-get install postgresql-15

# Create database
sudo -u postgres createdb football_db
sudo -u postgres createuser admin --pwprompt
```

**MongoDB:**
```bash
# Install MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
```

**Redis:**
```bash
# Install Redis
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis
```

### 3. Test Database Connections

```bash
# Test PostgreSQL
psql postgresql://admin:password123@localhost:5432/football_db -c "SELECT 1;"

# Test MongoDB
mongosh "mongodb://admin:password123@localhost:27017" --eval "db.runCommand({ ping: 1 })"

# Test Redis
redis-cli ping
# Should return: PONG
```

---

## Running Migrations

Migrations manage PostgreSQL schema changes using Alembic.

### Apply All Migrations

```bash
cd backend
alembic upgrade head
```

### Check Current Version

```bash
alembic current
```

### View Migration History

```bash
alembic history
```

### Rollback Last Migration

```bash
alembic downgrade -1
```

### Create New Migration

```bash
# After modifying models in api/models/postgres.py
alembic revision --autogenerate -m "description of changes"

# Review the generated file in alembic/versions/
# Then apply it:
alembic upgrade head
```

### Migration Files

Initial migration: `alembic/versions/20241109_initial_schema.py`

This creates:
- `users` table
- `leagues` table
- `teams` table
- `fixtures` table
- `user_favorites` table
- `crawl_jobs` table

---

## Seeding Data

The seed script populates the database with test data for development.

### Run Seed Script

```bash
cd backend
python scripts/seed_data.py
```

### What Gets Seeded

**PostgreSQL Tables:**
- 5 Major Leagues (Premier League, La Liga, Bundesliga, Serie A, Ligue 1)
- 15 Popular Teams (Man United, Liverpool, Real Madrid, etc.)
- 3 Sample Fixtures (past, live, upcoming)

**MongoDB Collections:**
- 2 Sample Matches with events and statistics

### Seed Data Script

Location: `backend/scripts/seed_data.py`

Features:
- ✅ Idempotent (can run multiple times safely)
- ✅ Checks for existing data
- ✅ Creates realistic test data
- ✅ Populates both PostgreSQL and MongoDB

---

## Testing the Setup

### Automated Test Script

```bash
cd backend
python scripts/test_setup.py
```

This verifies:
- ✅ PostgreSQL connection
- ✅ MongoDB connection
- ✅ Redis connection
- ✅ All tables created
- ✅ Seed data exists
- ✅ Indexes created

### Manual Verification

**Check PostgreSQL Tables:**

```bash
psql postgresql://admin:password123@localhost:5432/football_db

\dt  # List tables
SELECT COUNT(*) FROM leagues;  # Should return 5
SELECT COUNT(*) FROM teams;    # Should return 15
SELECT COUNT(*) FROM fixtures; # Should return 3
\q
```

**Check MongoDB Collections:**

```bash
mongosh "mongodb://admin:password123@localhost:27017"

use football_live
db.matches.count()  # Should return 2
db.matches.findOne()
exit
```

**Check Redis:**

```bash
redis-cli
PING  # Should return PONG
exit
```

---

## Troubleshooting

### Common Issues

#### 1. Connection Refused (PostgreSQL)

**Error:**
```
could not connect to server: Connection refused
```

**Solutions:**
```bash
# Check if PostgreSQL is running
docker compose ps postgres
# OR
sudo systemctl status postgresql

# Check logs
docker compose logs postgres
```

#### 2. Authentication Failed (MongoDB)

**Error:**
```
Authentication failed
```

**Solutions:**
```bash
# Verify credentials in .env match docker-compose.yml
# Restart MongoDB
docker compose restart mongodb
```

#### 3. Alembic Migration Fails

**Error:**
```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxxx'
```

**Solutions:**
```bash
# Reset alembic to base
alembic downgrade base

# Re-run migrations
alembic upgrade head
```

#### 4. Seed Script Fails

**Error:**
```
asyncpg.exceptions.UndefinedTableError: relation "leagues" does not exist
```

**Solutions:**
```bash
# Run migrations first
alembic upgrade head

# Then seed
python scripts/seed_data.py
```

### Health Check Commands

```bash
# Check all Docker services
docker compose ps

# View logs for specific service
docker compose logs -f postgres
docker compose logs -f mongodb
docker compose logs -f redis

# Restart a service
docker compose restart postgres
```

---

## Production Considerations

### Security

#### Change Default Credentials

```env
# .env (production)
DATABASE_URL=postgresql+asyncpg://prod_user:STRONG_PASSWORD@db-host:5432/football_prod
MONGO_URI=mongodb://prod_user:STRONG_PASSWORD@mongo-host:27017
SECRET_KEY=GENERATE_STRONG_SECRET_KEY_HERE
```

Generate secure password:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### Use SSL/TLS

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
MONGO_URI=mongodb://user:pass@host:27017/?tls=true
```

### Performance

#### PostgreSQL Tuning

```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 200;

-- Optimize for SSD
ALTER SYSTEM SET random_page_cost = 1.1;

-- Increase shared buffers
ALTER SYSTEM SET shared_buffers = '4GB';
```

#### MongoDB Indexes

```javascript
// Create indexes for common queries
db.matches.createIndex({ "status": 1, "match_date": -1 })
db.matches.createIndex({ "league.id": 1, "match_date": -1 })
db.matches.createIndex({ "external_id": 1 }, { unique: true })
```

#### Redis Configuration

```bash
# Increase max memory
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Backups

#### PostgreSQL Backup

```bash
# Create backup
pg_dump postgresql://user:pass@host:5432/football_db > backup_$(date +%Y%m%d).sql

# Restore backup
psql postgresql://user:pass@host:5432/football_db < backup_20241109.sql
```

#### MongoDB Backup

```bash
# Create backup
mongodump --uri="mongodb://user:pass@host:27017" --db=football_live --out=/backup/

# Restore backup
mongorestore --uri="mongodb://user:pass@host:27017" --db=football_live /backup/football_live/
```

#### Automated Backups

```bash
# Cron job (daily at 2 AM)
0 2 * * * /path/to/backup_script.sh
```

### Monitoring

#### Enable Query Logging

**PostgreSQL:**
```sql
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;
```

**MongoDB:**
```javascript
db.setProfilingLevel(1, { slowms: 100 })
```

#### Monitoring Tools

- **PostgreSQL**: pgAdmin, pg_stat_statements
- **MongoDB**: MongoDB Compass, mongotop
- **Redis**: redis-cli INFO, RedisInsight

---

## Database Migrations Workflow

### Development

```bash
# 1. Modify models in api/models/postgres.py
# 2. Generate migration
alembic revision --autogenerate -m "add_team_rating_field"

# 3. Review generated migration
cat alembic/versions/XXXX_add_team_rating_field.py

# 4. Apply migration
alembic upgrade head

# 5. Test changes
python scripts/test_setup.py
```

### Production

```bash
# 1. Backup database first!
pg_dump ... > backup_before_migration.sql

# 2. Run migration
alembic upgrade head

# 3. Verify migration
alembic current

# 4. If issues, rollback
alembic downgrade -1
```

---

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)
- [Redis Documentation](https://redis.io/documentation)

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs: `docker compose logs`
3. Check database status: `docker compose ps`
4. Open an issue on GitHub

---

**Last Updated**: 2024-11-09
**Database Version**: PostgreSQL 15, MongoDB 7, Redis 7
**Migration Version**: 001_initial
