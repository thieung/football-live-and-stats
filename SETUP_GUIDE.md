# 🚀 Football Live Score - Complete Setup Guide

This guide will walk you through setting up the Football Live Score application from scratch.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup Steps](#detailed-setup-steps)
4. [Verification](#verification)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** & npm - [Download](https://nodejs.org/)
- **Docker** & Docker Compose - [Download](https://www.docker.com/products/docker-desktop/)
- **Git** - [Download](https://git-scm.com/downloads)

### Verify Installations

```bash
python --version    # Should be 3.11 or higher
node --version      # Should be 18 or higher
npm --version       # Should be 9 or higher
docker --version    # Should be 20 or higher
git --version       # Should be 2.x or higher
```

---

## Quick Start

For experienced developers who want to get up and running quickly:

```bash
# 1. Clone the repository
git clone <repository-url>
cd football-live-and-stats

# 2. Start Docker services
cd backend
docker compose up -d postgres mongodb redis

# 3. Setup backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 4. Setup database
python scripts/setup_database.py

# 5. Start backend (in separate terminal)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# 6. Start Celery worker (in separate terminal)
celery -A tasks.celery_app worker --loglevel=info

# 7. Setup frontend (in separate terminal)
cd ../frontend
npm install
npm run dev

# 8. Access the application
# Frontend: http://localhost:5173
# Backend API Docs: http://localhost:8000/api/v1/docs
```

---

## Detailed Setup Steps

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd football-live-and-stats
```

### Step 2: Backend Setup

#### 2.1. Create Python Virtual Environment

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

#### 2.2. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- SQLAlchemy (PostgreSQL ORM)
- Motor (MongoDB driver)
- Redis client
- Celery (task queue)
- And many more dependencies

#### 2.3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings (optional for development)
# The default values work for local Docker setup
```

**Important environment variables:**

```env
# Database - PostgreSQL
DATABASE_URL=postgresql+asyncpg://admin:password@localhost:5432/football_db

# Database - MongoDB
MONGO_URI=mongodb://admin:password@localhost:27017
MONGO_DB_NAME=football_live

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret (change in production!)
SECRET_KEY=your-secret-key-here-change-in-production

# CORS (add your frontend URL)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Step 3: Start Docker Services

The application requires PostgreSQL, MongoDB, and Redis. We'll run them in Docker containers.

#### 3.1. Start Database Services

```bash
# Make sure you're in the backend directory
cd backend

# Start only the database services
docker compose up -d postgres mongodb redis

# Check if services are running
docker ps

# You should see:
# - football_postgres
# - football_mongodb
# - football_redis
```

#### 3.2. Wait for Services to be Healthy

```bash
# Check service health
docker compose ps

# All services should show "healthy" status
# This may take 10-30 seconds after starting
```

### Step 4: Database Setup

Now we'll create database tables and seed initial data.

#### 4.1. Automated Setup (Recommended)

```bash
# Run the automated setup script
python scripts/setup_database.py

# This script will:
# 1. Check Docker services are running
# 2. Run Alembic migrations to create tables
# 3. Seed initial data (leagues, teams, fixtures)
# 4. Verify the setup
```

#### 4.2. Manual Setup (Alternative)

If you prefer to run steps manually:

```bash
# 1. Run migrations to create tables
alembic upgrade head

# 2. Seed initial data
python scripts/seed_data.py

# 3. Verify setup
python scripts/test_setup.py
```

#### 4.3. Expected Output

After successful setup, you should see:

```
✅ All tests passed! Database setup is complete.

PostgreSQL: ✅ PASSED
MongoDB:    ✅ PASSED
Redis:      ✅ PASSED
```

### Step 5: Frontend Setup

#### 5.1. Install Node Dependencies

```bash
# Navigate to frontend directory
cd ../frontend

# Install dependencies
npm install

# This may take a few minutes
```

#### 5.2. Configure Frontend Environment (Optional)

```bash
# Copy example environment file
cp .env.example .env

# The default values work for local development
```

Default frontend `.env`:
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws
```

---

## Verification

### Verify Backend

1. **Check database tables exist:**

```bash
cd backend
python scripts/test_setup.py
```

2. **Check API is accessible:**

Start the backend and visit: http://localhost:8000/api/v1/docs

### Verify Frontend

```bash
cd frontend
npm run dev
```

Visit: http://localhost:5173

---

## Running the Application

You'll need **3 terminal windows** to run the full stack:

### Terminal 1: Backend API Server

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Access at:** http://localhost:8000/api/v1/docs

### Terminal 2: Celery Worker (Background Tasks)

```bash
cd backend
source venv/bin/activate  # Activate virtual environment
celery -A tasks.celery_app worker --loglevel=info
```

This runs:
- Live score crawlers
- Match event updates
- Periodic fixture fetching

### Terminal 3: Frontend Development Server

```bash
cd frontend
npm run dev
```

**Access at:** http://localhost:5173

---

## Application URLs

Once everything is running:

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Main application UI |
| Backend API | http://localhost:8000 | API base URL |
| API Documentation | http://localhost:8000/api/v1/docs | Interactive API docs (Swagger) |
| Alternative API Docs | http://localhost:8000/api/v1/redoc | ReDoc API documentation |
| WebSocket | ws://localhost:8000/ws | Real-time updates |

---

## Troubleshooting

### Docker Issues

**Problem:** `docker compose` command not found

**Solution:**
```bash
# Try with hyphen (older version)
docker-compose up -d

# Or install Docker Compose v2
# https://docs.docker.com/compose/install/
```

**Problem:** Port already in use (5432, 27017, or 6379)

**Solution:**
```bash
# Find what's using the port
lsof -i :5432  # macOS/Linux
netstat -ano | findstr :5432  # Windows

# Stop the conflicting service or change ports in docker-compose.yml
```

**Problem:** Docker services not healthy

**Solution:**
```bash
# Check logs
docker compose logs postgres
docker compose logs mongodb
docker compose logs redis

# Restart services
docker compose restart
```

### Database Issues

**Problem:** Alembic migration fails

**Solution:**
```bash
# Check database is accessible
docker compose ps

# Reset database (WARNING: deletes all data!)
docker compose down -v
docker compose up -d postgres mongodb redis

# Run migrations again
alembic upgrade head
```

**Problem:** Seed script fails

**Solution:**
```bash
# Check database connection in .env
# Ensure migrations ran successfully
alembic upgrade head

# Run seed script with error details
python scripts/seed_data.py
```

### Backend Issues

**Problem:** Import errors when starting backend

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Problem:** Database connection refused

**Solution:**
```bash
# Check Docker services are running
docker compose ps

# Check .env DATABASE_URL is correct
# Default: postgresql+asyncpg://admin:password@localhost:5432/football_db
```

### Frontend Issues

**Problem:** npm install fails

**Solution:**
```bash
# Clear cache and try again
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Problem:** Can't connect to backend API

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check CORS settings in backend/.env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Check frontend/.env has correct API URL
VITE_API_URL=http://localhost:8000/api/v1
```

### Celery Issues

**Problem:** Celery worker won't start

**Solution:**
```bash
# Check Redis is running
docker compose ps redis

# Check Celery broker URL in .env
CELERY_BROKER_URL=redis://localhost:6379/2

# Try with more verbose logging
celery -A tasks.celery_app worker --loglevel=debug
```

---

## Next Steps

Once setup is complete:

1. **Explore the API:** Visit http://localhost:8000/api/v1/docs
2. **Test endpoints:** Try the `/matches/live` and `/matches/today` endpoints
3. **Check WebSocket:** Connect to `ws://localhost:8000/ws` and subscribe to live updates
4. **Review the plan:** See `PLAN.md` for the full implementation roadmap
5. **Check status:** See `IMPLEMENTATION_STATUS.md` for what's completed and what's next

---

## Development Workflow

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Creating Database Migrations

When you modify database models:

```bash
cd backend
python scripts/create_migration.py "description of changes"
# or manually:
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Stopping Services

```bash
# Stop backend and Celery: Ctrl+C in their terminals

# Stop Docker services
cd backend
docker compose stop

# Stop and remove containers (keeps data)
docker compose down

# Stop and remove everything including data
docker compose down -v
```

---

## Production Deployment

For production deployment:

1. Change all passwords and secrets in `.env`
2. Set `DEBUG=False`
3. Use production-grade ASGI server (e.g., gunicorn)
4. Setup Nginx as reverse proxy
5. Enable SSL/HTTPS
6. Configure monitoring and logging
7. Setup automated backups
8. Review security settings

See `PLAN.md` section 10 for detailed deployment instructions.

---

## Support

For issues and questions:
- Check the troubleshooting section above
- Review `PLAN.md` for architecture details
- Check `IMPLEMENTATION_STATUS.md` for known issues
- Review the code documentation in each module

---

**Last Updated:** 2024-11-09
**Version:** 1.0.0
