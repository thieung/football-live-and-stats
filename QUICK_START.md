# ⚡ Quick Start - Football Live Score

Quick reference for common commands and workflows.

---

## 🚀 First Time Setup

```bash
# 1. Clone and enter directory
git clone <repo-url>
cd football-live-and-stats

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# 3. Start databases
docker compose up -d postgres mongodb redis

# 4. Setup database
python scripts/setup_database.py

# 5. Frontend setup
cd ../frontend
npm install
```

---

## 🏃 Daily Development

### Start Everything

**Terminal 1 - Databases:**
```bash
cd backend
docker compose up -d postgres mongodb redis
```

**Terminal 2 - Backend API:**
```bash
cd backend
source venv/bin/activate
uvicorn api.main:app --reload
```

**Terminal 3 - Celery Worker:**
```bash
cd backend
source venv/bin/activate
celery -A tasks.celery_app worker --loglevel=info
```

**Terminal 4 - Frontend:**
```bash
cd frontend
npm run dev
```

### Stop Everything

```bash
# Ctrl+C in each terminal
# Then stop databases:
cd backend
docker compose stop
```

---

## 📦 Common Commands

### Docker

```bash
# Start databases
docker compose up -d postgres mongodb redis

# Stop databases
docker compose stop

# View logs
docker compose logs -f postgres
docker compose logs -f mongodb
docker compose logs -f redis

# Restart a service
docker compose restart postgres

# Check status
docker compose ps

# Remove everything (⚠️ deletes data!)
docker compose down -v
```

### Database

```bash
cd backend

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Create new migration
python scripts/create_migration.py "description"
# or: alembic revision --autogenerate -m "description"

# Seed data
python scripts/seed_data.py

# Test database setup
python scripts/test_setup.py

# Full setup (migrations + seed + test)
python scripts/setup_database.py
```

### Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run development server
uvicorn api.main:app --reload

# Run with custom host/port
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Run Celery worker
celery -A tasks.celery_app worker --loglevel=info

# Run Celery beat (scheduler)
celery -A tasks.celery_app beat --loglevel=info

# Run tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=api tests/
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Lint code
npm run lint

# Format code
npm run format
```

---

## 🔗 Application URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/api/v1/docs |
| API Docs (ReDoc) | http://localhost:8000/api/v1/redoc |
| WebSocket | ws://localhost:8000/ws |

---

## 🧪 Testing Endpoints

### Using curl

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Get live matches
curl http://localhost:8000/api/v1/matches/live

# Get today's matches
curl http://localhost:8000/api/v1/matches/today

# Get leagues
curl http://localhost:8000/api/v1/leagues
```

### Using httpie (cleaner syntax)

```bash
# Install httpie: pip install httpie

# Health check
http GET localhost:8000/api/v1/health

# Register user
http POST localhost:8000/api/v1/auth/register \
  email=test@example.com username=testuser password=password123

# Login
http POST localhost:8000/api/v1/auth/login \
  username=testuser password=password123

# Get live matches
http GET localhost:8000/api/v1/matches/live

# With auth token
http GET localhost:8000/api/v1/matches/live \
  "Authorization: Bearer <your-token>"
```

---

## 🐛 Debugging

### Check Logs

```bash
# Docker logs
docker compose logs -f postgres
docker compose logs -f mongodb
docker compose logs -f redis

# Backend logs (if using uvicorn)
# Logs appear in the terminal where uvicorn is running

# Celery logs
# Logs appear in the terminal where celery worker is running
```

### Database Access

```bash
# PostgreSQL
docker exec -it football_postgres psql -U admin -d football_db

# Once connected:
\dt                  # List tables
\d users            # Describe users table
SELECT * FROM users; # Query users
\q                  # Quit

# MongoDB
docker exec -it football_mongodb mongosh -u admin -p password123

# Once connected:
use football_live                    # Switch to database
show collections                     # List collections
db.matches.find().pretty()          # Query matches
db.matches.countDocuments()         # Count documents
exit                                 # Quit

# Redis
docker exec -it football_redis redis-cli

# Once connected:
KEYS *              # List all keys
GET <key>           # Get value
PING                # Test connection
exit                # Quit
```

### Common Issues

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

**Database connection refused:**
```bash
# Check Docker services
docker compose ps

# Restart services
docker compose restart postgres mongodb redis
```

**Module not found errors:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 🔄 Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes, then:
git add .
git commit -m "feat: add feature description"

# Push to remote
git push origin feature/my-feature

# Create pull request on GitHub

# After PR is merged, update main
git checkout main
git pull origin main
```

---

## 📊 Database Maintenance

### Backup

```bash
# PostgreSQL backup
docker exec football_postgres pg_dump -U admin football_db > backup.sql

# Restore PostgreSQL
docker exec -i football_postgres psql -U admin football_db < backup.sql

# MongoDB backup
docker exec football_mongodb mongodump \
  --username admin \
  --password password123 \
  --db football_live \
  --out /tmp/backup

# MongoDB restore
docker exec football_mongodb mongorestore \
  --username admin \
  --password password123 \
  --db football_live \
  /tmp/backup/football_live
```

### Reset Database

```bash
# ⚠️ WARNING: This deletes all data!

# Method 1: Drop and recreate containers
docker compose down -v
docker compose up -d postgres mongodb redis
python scripts/setup_database.py

# Method 2: Drop and recreate tables (PostgreSQL only)
alembic downgrade base
alembic upgrade head
python scripts/seed_data.py
```

---

## 🎯 Development Tips

1. **Use API documentation:** http://localhost:8000/api/v1/docs is interactive!
2. **Monitor Celery tasks:** Check the Celery worker terminal for task execution
3. **WebSocket testing:** Use tools like `wscat` or browser console
4. **Database GUI tools:** Consider using pgAdmin, MongoDB Compass, or RedisInsight
5. **API testing:** Postman or Insomnia for testing complex requests

---

## 📚 Additional Resources

- **Full Documentation:** See `SETUP_GUIDE.md`
- **Implementation Plan:** See `PLAN.md`
- **Current Status:** See `IMPLEMENTATION_STATUS.md`
- **Database Schema:** See `DATABASE_SETUP.md`
- **Backend README:** See `backend/README.md`

---

**Need Help?** Check the troubleshooting section in `SETUP_GUIDE.md`
