# Football Live Score - Backend

Real-time football live scores and statistics API built with FastAPI and Python.

## Features

- ⚡ **FastAPI** - Modern, fast web framework
- 🔄 **Real-time Updates** - WebSocket support for live scores
- 🗄️ **Hybrid Database** - PostgreSQL + MongoDB + Redis
- 🕷️ **Web Crawling** - Scrapy, Playwright, BeautifulSoup
- 📊 **Background Tasks** - Celery for distributed crawling
- 🔐 **JWT Authentication** - Secure user authentication
- 📝 **API Documentation** - Auto-generated OpenAPI docs

## Tech Stack

- **Framework**: FastAPI
- **Databases**: PostgreSQL (relational), MongoDB (flexible), Redis (cache/pub-sub)
- **Task Queue**: Celery + Redis
- **Web Scraping**: Scrapy, Playwright, BeautifulSoup, httpx
- **Authentication**: JWT (python-jose, passlib)
- **ORM**: SQLAlchemy (async), Motor (async MongoDB)

## Project Structure

```
backend/
├── api/
│   ├── core/
│   │   ├── config.py          # Application settings
│   │   ├── database.py        # Database connections
│   │   └── security.py        # Authentication utilities
│   ├── models/
│   │   └── postgres.py        # SQLAlchemy models
│   ├── routes/
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── matches.py         # Match endpoints
│   │   ├── leagues.py         # League endpoints
│   │   ├── teams.py           # Team endpoints
│   │   ├── users.py           # User endpoints
│   │   └── websocket.py       # WebSocket endpoint
│   ├── schemas/
│   │   ├── user.py            # User Pydantic models
│   │   └── match.py           # Match Pydantic models
│   ├── services/
│   │   ├── match_service.py   # Match business logic
│   │   └── league_service.py  # League business logic
│   └── main.py                # FastAPI application
├── crawlers/
│   ├── base.py                # Base crawler
│   ├── flashscore.py          # FlashScore crawler
│   └── parsers/               # Data parsers
├── tasks/
│   ├── celery_app.py          # Celery configuration
│   └── live_scores.py         # Crawling tasks
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker image
├── docker-compose.yml         # Docker Compose config
└── .env.example               # Environment variables template
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- PostgreSQL 15+
- MongoDB 7+
- Redis 7+

### Using Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd backend
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Check logs**
```bash
docker-compose logs -f backend
```

5. **Access the API**
- API: http://localhost:8000
- Docs: http://localhost:8000/api/v1/docs
- Health: http://localhost:8000/health

### Manual Setup (Without Docker)

1. **Install dependencies**
```bash
pip install -r requirements.txt
playwright install chromium
```

2. **Setup databases**
- Install and start PostgreSQL, MongoDB, Redis
- Create database: `createdb football_db`

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database URLs
```

4. **Run migrations** (optional - tables auto-created on startup)
```bash
alembic upgrade head
```

5. **Start the API server**
```bash
uvicorn api.main:app --reload
```

6. **Start Celery worker** (in another terminal)
```bash
celery -A tasks.celery_app worker --loglevel=info
```

7. **Start Celery beat** (in another terminal)
```bash
celery -A tasks.celery_app beat --loglevel=info
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout

### Matches
- `GET /api/v1/matches/live` - Get live matches
- `GET /api/v1/matches/today` - Get today's matches
- `GET /api/v1/matches/upcoming` - Get upcoming matches
- `GET /api/v1/matches/{id}` - Get match details
- `GET /api/v1/matches/{id}/events` - Get match events
- `GET /api/v1/matches/{id}/stats` - Get match statistics

### Leagues
- `GET /api/v1/leagues` - List all leagues
- `GET /api/v1/leagues/{id}` - Get league details
- `GET /api/v1/leagues/{id}/table` - Get league standings
- `GET /api/v1/leagues/{id}/fixtures` - Get league fixtures

### Teams
- `GET /api/v1/teams/{id}` - Get team details
- `GET /api/v1/teams/{id}/fixtures` - Get team fixtures

### Users
- `GET /api/v1/users/favorites` - Get user favorites
- `POST /api/v1/users/favorites` - Add favorite
- `DELETE /api/v1/users/favorites/{id}` - Remove favorite

### WebSocket
- `WS /ws` - WebSocket connection for real-time updates

## WebSocket Usage

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

// Subscribe to channels
ws.send(JSON.stringify({
    action: 'subscribe',
    channels: ['match:12345', 'live:all']
}));

// Receive updates
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Update:', data);
};
```

## Development

### Run tests
```bash
pytest
```

### Code formatting
```bash
black .
```

### Type checking
```bash
mypy .
```

### Linting
```bash
flake8 .
```

## Database Migrations

Using Alembic for PostgreSQL migrations:

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `SECRET_KEY` - JWT secret key (change in production!)
- `DATABASE_URL` - PostgreSQL connection string
- `MONGO_URI` - MongoDB connection string
- `REDIS_URL` - Redis connection string
- `DEBUG` - Enable debug mode (set to False in production)

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use strong `SECRET_KEY`
3. Use production-grade databases (not Docker containers)
4. Enable HTTPS
5. Set up proper logging and monitoring
6. Use process manager (supervisor, systemd)
7. Configure reverse proxy (Nginx)
8. Set up rate limiting
9. Enable CORS only for your frontend domain

## License

MIT

## Contributing

Pull requests are welcome!
