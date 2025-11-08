# ⚽ Football Live Score & Stats Web Application

A comprehensive real-time football live score tracking application with Python backend for data crawling and SvelteKit frontend for beautiful, responsive UI.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Development](#development)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Features
- 🔴 **Real-time Live Scores** - WebSocket-powered live updates
- ⚡ **Fast Performance** - Optimized with Redis caching
- 📊 **Match Statistics** - Detailed stats, events, lineups
- 🏆 **League Tables** - Current standings and rankings
- 📅 **Fixtures** - Upcoming and past matches
- 👤 **User Accounts** - Authentication with JWT
- ⭐ **Favorites** - Save your favorite teams/leagues
- 📱 **Responsive Design** - Works on all devices

### Technical Features
- **Distributed Crawling** - Celery-based background tasks
- **Hybrid Database** - PostgreSQL + MongoDB + Redis
- **Anti-Detection** - Proxy rotation, user-agent rotation
- **Auto-Retry** - Exponential backoff for failed requests
- **Monitoring** - Prometheus metrics, structured logging
- **Scalable** - Microservices architecture

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND LAYER                      │
│  SvelteKit App (SSR/CSR) + WebSocket Client            │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/REST + WebSocket
┌────────────────────────▼────────────────────────────────┐
│                   API GATEWAY (Nginx)                   │
└────────────────────────┬────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼────────┐              ┌────────▼─────────┐
│  FastAPI App   │              │  WebSocket Server│
│  (REST API)    │              │  (Real-time)     │
└───────┬────────┘              └────────┬─────────┘
        │                                │
        └────────────┬───────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│              DATABASE & CACHE LAYER                  │
│  ┌────────────┐  ┌──────────┐  ┌──────────┐        │
│  │ PostgreSQL │  │ MongoDB  │  │  Redis   │        │
│  │ (metadata) │  │ (matches)│  │ (cache)  │        │
│  └────────────┘  └──────────┘  └──────────┘        │
└──────────────────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────┐
│                 CRAWLING LAYER                       │
│  Celery Workers + Scrapy + Playwright               │
│  ├─ Live Score Crawler (every 30s)                  │
│  ├─ Match Events Crawler (every 10s)                │
│  ├─ Fixtures Crawler (daily)                        │
│  └─ Stats Crawler (hourly)                          │
└──────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (async Python web framework)
- **Task Queue**: Celery + Redis
- **Web Scraping**: Scrapy, Playwright, BeautifulSoup, httpx
- **Databases**:
  - PostgreSQL (users, teams, leagues)
  - MongoDB (matches, events, stats)
  - Redis (cache, pub/sub, broker)
- **Authentication**: JWT (python-jose, passlib)
- **ORM**: SQLAlchemy (async), Motor (async MongoDB)

### Frontend
- **Framework**: SvelteKit (SSR + CSR)
- **Styling**: TailwindCSS
- **HTTP Client**: Axios
- **Real-time**: Native WebSocket
- **Build Tool**: Vite

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **Monitoring**: Prometheus + Grafana (optional)
- **Logging**: Structlog (structured JSON logs)

## 📁 Project Structure

```
football-live-and-stats/
├── backend/                    # Python backend
│   ├── api/                    # FastAPI application
│   │   ├── core/              # Config, database, security
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routes/            # API endpoints
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   └── main.py            # FastAPI app entry
│   ├── crawlers/              # Web crawlers
│   │   ├── base.py            # Base crawler class
│   │   ├── flashscore.py      # FlashScore crawler
│   │   └── parsers/           # HTML parsers
│   ├── tasks/                 # Celery tasks
│   │   ├── celery_app.py      # Celery config
│   │   ├── live_scores.py     # Live score tasks
│   │   ├── fixtures.py        # Fixture tasks
│   │   └── stats.py           # Stats tasks
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile             # Backend Docker image
│   └── docker-compose.yml     # Full stack setup
│
├── frontend/                   # SvelteKit frontend
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/    # Svelte components
│   │   │   ├── stores/        # State management
│   │   │   └── types/         # TypeScript types
│   │   ├── routes/            # SvelteKit pages
│   │   ├── app.css            # Global styles
│   │   └── app.html           # HTML template
│   ├── package.json           # Node dependencies
│   ├── svelte.config.js       # SvelteKit config
│   ├── tailwind.config.js     # Tailwind config
│   └── vite.config.ts         # Vite config
│
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (recommended)
- OR:
  - Python 3.11+
  - Node.js 18+
  - PostgreSQL 15+
  - MongoDB 7+
  - Redis 7+

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd football-live-and-stats
```

2. **Create environment files**
```bash
# Backend
cd backend
cp .env.example .env
# Edit .env with your configuration

# Frontend
cd ../frontend
cp .env.example .env
# Edit .env (use default values for Docker)
```

3. **Start all services**
```bash
cd backend
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Setup environment
cp .env.example .env
# Edit .env with your database URLs

# Start services
uvicorn api.main:app --reload  # Terminal 1
celery -A tasks.celery_app worker --loglevel=info  # Terminal 2
celery -A tasks.celery_app beat --loglevel=info  # Terminal 3
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env
# Edit .env with backend URL

# Start dev server
npm run dev
```

## 💻 Development

### Backend Development

```bash
cd backend

# Run tests
pytest

# Format code
black .

# Type checking
mypy .

# Linting
flake8 .

# Database migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### Frontend Development

```bash
cd frontend

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run check

# Linting
npm run lint

# Format code
npm run format
```

### Adding New Crawlers

1. Create new crawler in `backend/crawlers/`
2. Extend `BaseCrawler` class
3. Implement required methods: `crawl_match()`, `crawl_fixtures()`, etc.
4. Add Celery task in `backend/tasks/`
5. Update Celery beat schedule

Example:
```python
# backend/crawlers/new_source.py
from crawlers.base import BaseCrawler

class NewSourceCrawler(BaseCrawler):
    async def crawl_match(self, match_id: str):
        # Implementation
        pass
```

## 📊 API Documentation

API documentation is automatically generated by FastAPI:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

### Key Endpoints

```
Authentication:
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/me

Matches:
GET    /api/v1/matches/live
GET    /api/v1/matches/today
GET    /api/v1/matches/{id}

Leagues:
GET    /api/v1/leagues
GET    /api/v1/leagues/{id}/table

WebSocket:
WS     /ws
```

## 🌐 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in backend `.env`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production databases (not Docker)
- [ ] Enable HTTPS (SSL/TLS)
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure CORS for production domain
- [ ] Set up monitoring (Prometheus + Grafana)
- [ ] Configure log aggregation
- [ ] Set up automated backups
- [ ] Configure rate limiting
- [ ] Use CDN for static assets

### Deployment Options

#### AWS

- **Compute**: ECS Fargate / EC2
- **Database**: RDS PostgreSQL, DocumentDB/MongoDB Atlas
- **Cache**: ElastiCache Redis
- **Load Balancer**: ALB
- **Static Assets**: S3 + CloudFront

#### Vercel (Frontend)

```bash
cd frontend
npm install -g vercel
vercel
```

#### Heroku (Backend)

```bash
cd backend
heroku create
heroku addons:create heroku-postgresql
heroku addons:create heroku-redis
git push heroku main
```

## 📈 Performance

### Benchmarks (Expected)

- API Response Time: < 100ms (p95)
- WebSocket Latency: < 50ms
- Live Score Update Delay: 10-30s
- Page Load Time: < 2s (FCP)
- Concurrent Users: 10,000+

### Optimization Tips

1. **Caching**: Use Redis for frequently accessed data
2. **Database Indexing**: Optimize MongoDB and PostgreSQL queries
3. **CDN**: Serve static assets via CDN
4. **Compression**: Enable gzip/brotli compression
5. **Connection Pooling**: Configure database connection pools
6. **Lazy Loading**: Implement infinite scroll for large lists

## 🔒 Security

- JWT authentication with secure token storage
- Password hashing with bcrypt
- SQL injection prevention (parameterized queries)
- XSS protection (input sanitization)
- CORS configuration
- Rate limiting on API endpoints
- Environment variables for secrets
- HTTPS in production

## 🐛 Troubleshooting

### Common Issues

**Issue**: Database connection failed
- Check if databases are running: `docker-compose ps`
- Verify connection strings in `.env`

**Issue**: Celery worker not processing tasks
- Check Redis connection
- Verify Celery broker URL
- Check worker logs: `docker-compose logs celery_worker`

**Issue**: WebSocket not connecting
- Verify WebSocket URL in frontend `.env`
- Check CORS configuration
- Inspect browser console for errors

**Issue**: Crawling fails with 403 error
- Enable proxy rotation
- Check user-agent rotation
- Verify source website is accessible

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- Data sources: FlashScore, LiveScore, SofaScore
- Icons: Heroicons
- Inspiration: Various football score websites

---

**⚠️ Disclaimer**: This project is for educational purposes. Be respectful of website terms of service when crawling data. Consider using official APIs when available.

**🎯 Roadmap**:
- [ ] Player statistics and profiles
- [ ] Match predictions using ML
- [ ] Mobile apps (React Native)
- [ ] Push notifications
- [ ] Social features (comments, predictions)
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Live match commentary
- [ ] Video highlights integration
