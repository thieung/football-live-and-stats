# ⚽ FOOTBALL LIVE SCORE - COMPLETE IMPLEMENTATION PLAN

> Comprehensive step-by-step plan for building a real-time football live score web application with Python backend crawling and SvelteKit frontend.

---

## 📑 TABLE OF CONTENTS

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Database Design](#3-database-design)
4. [Backend API Design](#4-backend-api-design)
5. [Crawling Strategy](#5-crawling-strategy)
6. [Real-time Implementation](#6-real-time-implementation)
7. [Frontend Design](#7-frontend-design)
8. [Implementation Roadmap](#8-implementation-roadmap)
9. [Testing Strategy](#9-testing-strategy)
10. [Deployment Plan](#10-deployment-plan)
11. [Performance Optimization](#11-performance-optimization)
12. [Security Implementation](#12-security-implementation)
13. [Monitoring & Maintenance](#13-monitoring--maintenance)

---

## 1. PROJECT OVERVIEW

### 1.1 Project Goals

- ✅ Build real-time football live score tracking application
- ✅ Crawl data from multiple external sources
- ✅ Provide WebSocket-based live updates
- ✅ Support multiple leagues and competitions
- ✅ Scalable microservices architecture
- ✅ Production-ready with monitoring

### 1.2 Tech Stack

#### Backend Stack
```
Language: Python 3.11+
Framework: FastAPI (async web framework)

Web Scraping:
├── Scrapy (structured crawling framework)
├── BeautifulSoup4 (HTML parsing)
├── Playwright (JavaScript-rendered pages)
├── httpx (async HTTP client)
└── lxml (fast XML/HTML processing)

Databases:
├── PostgreSQL 15+ (relational data: users, teams, leagues)
├── MongoDB 7+ (flexible schema: matches, events, stats)
└── Redis 7+ (cache, pub/sub, session storage)

Task Queue:
├── Celery (distributed task processing)
├── Redis (message broker)
└── Celery Beat (periodic task scheduler)

Authentication:
├── JWT (JSON Web Tokens)
├── python-jose (JWT implementation)
└── passlib + bcrypt (password hashing)

ORM/ODM:
├── SQLAlchemy 2.0+ (async PostgreSQL ORM)
└── Motor (async MongoDB driver)
```

#### Frontend Stack
```
Framework: SvelteKit (SSR + CSR)
Styling: TailwindCSS 3+
Language: TypeScript
HTTP Client: Axios
Date Library: date-fns
Build Tool: Vite
WebSocket: Native WebSocket API
```

#### Infrastructure Stack
```
Containerization: Docker + Docker Compose
Reverse Proxy: Nginx
CI/CD: GitHub Actions (optional)
Monitoring: Prometheus + Grafana
Logging: Structlog (JSON logging)
Process Manager: Supervisor / systemd
```

### 1.3 Key Features

#### Core Features (MVP)
- [x] Real-time live scores
- [x] Today's matches
- [x] Upcoming fixtures
- [x] League standings/tables
- [x] Match details (score, events, stats)
- [x] User registration & login
- [x] Favorite teams/leagues
- [x] WebSocket live updates

#### Future Features (Post-MVP)
- [ ] Player statistics & profiles
- [ ] Team detailed pages
- [ ] Match predictions (ML-based)
- [ ] Push notifications
- [ ] Social features (comments, voting)
- [ ] Video highlights integration
- [ ] Mobile apps (React Native)
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Advanced search & filters

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Browser   │  │   Mobile    │  │   Tablet    │            │
│  │   (Web)     │  │   (Future)  │  │   (Web)     │            │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│         │                 │                 │                   │
└─────────┼─────────────────┼─────────────────┼───────────────────┘
          │                 │                 │
          └─────────────────┴─────────────────┘
                            │
                  HTTP/HTTPS + WebSocket
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    API GATEWAY LAYER                             │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Nginx (Reverse Proxy)                        │ │
│  │  ├─ Load Balancing                                        │ │
│  │  ├─ Rate Limiting                                         │ │
│  │  ├─ SSL Termination                                       │ │
│  │  ├─ Static File Serving                                   │ │
│  │  └─ Request Routing                                       │ │
│  └───────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
          ┌─────────────────┴─────────────────┐
          │                                   │
┌─────────▼──────────┐              ┌────────▼─────────────┐
│   FastAPI App      │              │  WebSocket Server    │
│   (REST API)       │              │  (Real-time)         │
│                    │              │                      │
│ ├─ Auth Routes     │              │ ├─ Connection Mgmt  │
│ ├─ Match Routes    │              │ ├─ Channel Sub/Pub  │
│ ├─ League Routes   │              │ ├─ Message Routing  │
│ ├─ Team Routes     │              │ └─ Heartbeat/Ping   │
│ ├─ User Routes     │              │                      │
│ └─ Admin Routes    │              │                      │
└─────────┬──────────┘              └────────┬─────────────┘
          │                                   │
          └─────────────────┬─────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                           │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                    Service Layer                           ││
│  │                                                            ││
│  │  ├─ MatchService                                          ││
│  │  │   ├─ get_live_matches()                                ││
│  │  │   ├─ get_match_details()                               ││
│  │  │   ├─ update_match_score()                              ││
│  │  │   └─ add_match_event()                                 ││
│  │  │                                                         ││
│  │  ├─ LeagueService                                         ││
│  │  │   ├─ get_league_table()                                ││
│  │  │   ├─ get_league_fixtures()                             ││
│  │  │   └─ update_standings()                                ││
│  │  │                                                         ││
│  │  ├─ CrawlerService                                        ││
│  │  │   ├─ schedule_crawl_task()                             ││
│  │  │   ├─ get_crawl_status()                                ││
│  │  │   └─ handle_crawl_result()                             ││
│  │  │                                                         ││
│  │  ├─ NotificationService                                   ││
│  │  │   ├─ broadcast_match_update()                          ││
│  │  │   ├─ notify_goal_event()                               ││
│  │  │   └─ send_user_notification()                          ││
│  │  │                                                         ││
│  │  └─ CacheService                                          ││
│  │      ├─ get_cached_data()                                 ││
│  │      ├─ set_cache()                                       ││
│  │      └─ invalidate_cache()                                ││
│  └────────────────────────────────────────────────────────────┘│
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐  ┌────────▼────────┐  ┌──────▼──────┐
│ PostgreSQL   │  │   MongoDB       │  │   Redis     │
│              │  │                 │  │             │
│ ├─ Users     │  │ ├─ Matches      │  │ ├─ Cache    │
│ ├─ Leagues   │  │ ├─ Events       │  │ ├─ Pub/Sub  │
│ ├─ Teams     │  │ ├─ Statistics   │  │ ├─ Sessions │
│ ├─ Fixtures  │  │ ├─ Tables       │  │ └─ Queues   │
│ └─ Favorites │  │ └─ Raw Data     │  │             │
└──────────────┘  └─────────────────┘  └──────┬──────┘
                                               │
                                               │ Broker
┌──────────────────────────────────────────────▼──────────────────┐
│                      CRAWLING LAYER                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │              Celery Workers (Distributed)                  ││
│  │                                                            ││
│  │  Worker 1:                Worker 2:         Worker N:     ││
│  │  ├─ Live Scores          ├─ Fixtures       ├─ Stats      ││
│  │  ├─ Match Events         ├─ Tables         └─ Players    ││
│  │  └─ Team Data            └─ News                          ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │              Celery Beat (Scheduler)                       ││
│  │                                                            ││
│  │  ├─ Live Scores Task (every 30s)                          ││
│  │  ├─ Match Events Task (every 10s)                         ││
│  │  ├─ Fixtures Task (daily at 2 AM)                         ││
│  │  ├─ League Tables Task (hourly)                           ││
│  │  └─ Team Stats Task (every 6 hours)                       ││
│  └────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐│
│  │                 Scraping Engines                           ││
│  │                                                            ││
│  │  ├─ FlashScoreCrawler (Playwright - JS rendering)        ││
│  │  ├─ LiveScoreCrawler (httpx - Fast static)               ││
│  │  ├─ SofaScoreCrawler (API-based)                         ││
│  │  └─ ESPNCrawler (BeautifulSoup - Parsing)               ││
│  └────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow Architecture

#### 2.2.1 Live Score Update Flow

```
Step 1: Crawling
┌─────────────────────────────────────────────────────────┐
│ Celery Beat triggers crawl task (every 30s)            │
│         ↓                                               │
│ Celery Worker picks up task                            │
│         ↓                                               │
│ FlashScoreCrawler.crawl_match(match_id)               │
│         ↓                                               │
│ Fetch HTML from source                                 │
│         ↓                                               │
│ Parse score, minute, events                            │
└─────────────────┬───────────────────────────────────────┘
                  │
Step 2: Data Processing
┌─────────────────▼───────────────────────────────────────┐
│ Validate crawled data                                   │
│         ↓                                               │
│ Compare with existing data (detect changes)            │
│         ↓                                               │
│ MatchService.update_match(match_id, data)             │
│         ↓                                               │
│ Save to MongoDB (matches collection)                   │
└─────────────────┬───────────────────────────────────────┘
                  │
Step 3: Cache Update
┌─────────────────▼───────────────────────────────────────┐
│ CacheService.invalidate_cache(match_id)                │
│         ↓                                               │
│ Update Redis cache with new data                       │
│         ↓                                               │
│ Set TTL (30 seconds for live matches)                  │
└─────────────────┬───────────────────────────────────────┘
                  │
Step 4: Real-time Notification
┌─────────────────▼───────────────────────────────────────┐
│ NotificationService.broadcast_update()                  │
│         ↓                                               │
│ Publish to Redis channel: "match:{id}"                 │
│         ↓                                               │
│ WebSocket server listening to Redis                    │
│         ↓                                               │
│ Broadcast to subscribed WebSocket clients              │
└─────────────────┬───────────────────────────────────────┘
                  │
Step 5: Client Update
┌─────────────────▼───────────────────────────────────────┐
│ Browser receives WebSocket message                      │
│         ↓                                               │
│ Update Svelte store                                     │
│         ↓                                               │
│ Reactive UI updates automatically                       │
└─────────────────────────────────────────────────────────┘
```

#### 2.2.2 User Request Flow

```
GET /api/v1/matches/live
         ↓
┌────────────────────────────────────────┐
│ 1. Nginx receives request              │
│    ├─ Check rate limit                 │
│    ├─ Forward to FastAPI               │
└────────┬───────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ 2. FastAPI route handler               │
│    ├─ Extract query params             │
│    ├─ Validate auth token (optional)   │
└────────┬───────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ 3. Check Redis cache                   │
│    ├─ Key: "live_matches"              │
│    ├─ If HIT: Return cached data       │
│    └─ If MISS: Continue to DB          │
└────────┬───────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ 4. Query MongoDB                       │
│    ├─ matches.find({status: "live"})   │
│    ├─ Sort by match_date               │
│    └─ Limit results                    │
└────────┬───────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ 5. Transform data                      │
│    ├─ Map to Pydantic schema           │
│    ├─ Serialize to JSON                │
└────────┬───────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ 6. Cache result                        │
│    ├─ Store in Redis (TTL: 30s)        │
└────────┬───────────────────────────────┘
         ↓
┌────────────────────────────────────────┐
│ 7. Return response                     │
│    └─ HTTP 200 + JSON body             │
└────────────────────────────────────────┘
```

### 2.3 Component Breakdown

#### 2.3.1 Backend Components

```
backend/
│
├── api/                        # FastAPI Application
│   ├── core/                   # Core functionality
│   │   ├── config.py          # Settings (Pydantic BaseSettings)
│   │   ├── database.py        # DB connections (PostgreSQL, MongoDB, Redis)
│   │   └── security.py        # Auth utilities (JWT, password hashing)
│   │
│   ├── models/                 # Database models
│   │   ├── postgres.py        # SQLAlchemy ORM models
│   │   └── mongo.py           # MongoDB document schemas (optional)
│   │
│   ├── routes/                 # API endpoints
│   │   ├── auth.py            # POST /register, /login, /logout
│   │   ├── matches.py         # GET /live, /today, /{id}
│   │   ├── leagues.py         # GET /, /{id}, /{id}/table
│   │   ├── teams.py           # GET /{id}, /{id}/fixtures
│   │   ├── users.py           # GET /favorites, POST /favorites
│   │   ├── websocket.py       # WS /ws (WebSocket endpoint)
│   │   └── admin.py           # Admin endpoints (crawl triggers)
│   │
│   ├── schemas/                # Pydantic schemas (request/response)
│   │   ├── user.py            # UserCreate, UserResponse, Token
│   │   ├── match.py           # MatchResponse, MatchQuery
│   │   ├── league.py          # LeagueResponse, TableResponse
│   │   └── team.py            # TeamResponse
│   │
│   ├── services/               # Business logic
│   │   ├── match_service.py   # Match CRUD operations
│   │   ├── league_service.py  # League operations
│   │   ├── cache_service.py   # Redis caching
│   │   └── notification_service.py  # WebSocket broadcasting
│   │
│   └── main.py                 # FastAPI app initialization
│
├── crawlers/                   # Web scraping
│   ├── base.py                # BaseCrawler abstract class
│   ├── flashscore.py          # FlashScore implementation
│   ├── livescore.py           # LiveScore implementation
│   ├── sofascore.py           # SofaScore implementation
│   │
│   ├── parsers/               # HTML/JSON parsers
│   │   ├── match_parser.py   # Parse match data
│   │   ├── event_parser.py   # Parse events
│   │   └── stats_parser.py   # Parse statistics
│   │
│   └── middlewares/           # Crawler middlewares
│       ├── proxy.py          # Proxy rotation
│       ├── retry.py          # Retry logic
│       └── rate_limit.py     # Rate limiting per domain
│
├── tasks/                     # Celery tasks
│   ├── celery_app.py         # Celery configuration + beat schedule
│   ├── live_scores.py        # Live score crawling tasks
│   ├── fixtures.py           # Fixture crawling tasks
│   ├── stats.py              # Statistics crawling tasks
│   └── utils.py              # Task utilities
│
├── tests/                     # Test suite
│   ├── test_api/             # API endpoint tests
│   ├── test_crawlers/        # Crawler tests
│   ├── test_services/        # Service layer tests
│   └── conftest.py           # Pytest fixtures
│
├── alembic/                   # Database migrations
│   ├── versions/             # Migration files
│   └── env.py                # Alembic config
│
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Backend Docker image
├── docker-compose.yml         # Full stack setup
└── .env.example               # Environment variables template
```

#### 2.3.2 Frontend Components

```
frontend/
│
├── src/
│   ├── lib/                   # Reusable code
│   │   │
│   │   ├── components/        # Svelte components
│   │   │   ├── MatchCard.svelte        # Display single match
│   │   │   ├── MatchList.svelte        # List of matches
│   │   │   ├── LeagueTable.svelte      # League standings
│   │   │   ├── LiveIndicator.svelte    # Live badge/pulse
│   │   │   ├── LoadingSpinner.svelte   # Loading state
│   │   │   ├── ErrorMessage.svelte     # Error display
│   │   │   ├── Header.svelte           # App header
│   │   │   ├── Footer.svelte           # App footer
│   │   │   ├── Navbar.svelte           # Navigation
│   │   │   └── Modal.svelte            # Modal dialog
│   │   │
│   │   ├── stores/            # State management
│   │   │   ├── websocket.ts   # WebSocket connection store
│   │   │   ├── matches.ts     # Match data store
│   │   │   ├── leagues.ts     # League data store
│   │   │   ├── auth.ts        # Authentication store
│   │   │   └── ui.ts          # UI state (modals, toasts)
│   │   │
│   │   ├── types/             # TypeScript types
│   │   │   ├── match.ts       # Match interfaces
│   │   │   ├── league.ts      # League interfaces
│   │   │   ├── team.ts        # Team interfaces
│   │   │   └── user.ts        # User interfaces
│   │   │
│   │   ├── utils/             # Utility functions
│   │   │   ├── api.ts         # API client (Axios wrapper)
│   │   │   ├── date.ts        # Date formatting
│   │   │   ├── validation.ts  # Form validation
│   │   │   └── constants.ts   # App constants
│   │   │
│   │   └── config/            # Configuration
│   │       └── env.ts         # Environment variables
│   │
│   ├── routes/                # SvelteKit pages
│   │   ├── +layout.svelte             # Root layout
│   │   ├── +page.svelte               # Home page (live scores)
│   │   │
│   │   ├── matches/
│   │   │   ├── +page.svelte           # All matches
│   │   │   └── [id]/
│   │   │       └── +page.svelte       # Match detail page
│   │   │
│   │   ├── leagues/
│   │   │   ├── +page.svelte           # All leagues
│   │   │   └── [id]/
│   │   │       ├── +page.svelte       # League detail
│   │   │       ├── table/
│   │   │       │   └── +page.svelte   # League table
│   │   │       └── fixtures/
│   │   │           └── +page.svelte   # League fixtures
│   │   │
│   │   ├── teams/
│   │   │   └── [id]/
│   │   │       └── +page.svelte       # Team page
│   │   │
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   │   └── +page.svelte       # Login page
│   │   │   └── register/
│   │   │       └── +page.svelte       # Register page
│   │   │
│   │   └── profile/
│   │       └── +page.svelte           # User profile
│   │
│   ├── app.css                # Global styles (Tailwind)
│   └── app.html               # HTML template
│
├── static/                    # Static assets
│   ├── favicon.png
│   └── images/
│
├── package.json               # Node dependencies
├── svelte.config.js           # SvelteKit config
├── tailwind.config.js         # Tailwind config
├── vite.config.ts             # Vite config
├── tsconfig.json              # TypeScript config
└── .env.example               # Environment variables
```

---

## 3. DATABASE DESIGN

### 3.1 PostgreSQL Schema (Relational Data)

#### 3.1.1 Users Table

```sql
-- Users and authentication
CREATE TABLE users (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Authentication
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,

    -- Profile
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),

    -- Preferences
    favorite_league_id UUID,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,

    -- Indexes
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE is_active = TRUE;
```

#### 3.1.2 Leagues Table

```sql
-- Football leagues/competitions
CREATE TABLE leagues (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- External reference
    external_id VARCHAR(100) UNIQUE,
    source VARCHAR(50), -- 'flashscore', 'livescore', etc.

    -- Basic info
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    country VARCHAR(100),
    country_code VARCHAR(3), -- ISO 3166-1 alpha-3

    -- Media
    logo_url VARCHAR(500),
    banner_url VARCHAR(500),

    -- Season info
    season VARCHAR(20), -- "2024/2025"
    start_date DATE,
    end_date DATE,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    priority INT DEFAULT 0, -- Display order

    -- Metadata
    league_type VARCHAR(50), -- 'domestic', 'international', 'cup'
    tier INT, -- League tier (1 = top tier)
    num_teams INT,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_leagues_country ON leagues(country);
CREATE INDEX idx_leagues_is_active ON leagues(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_leagues_priority ON leagues(priority DESC);
CREATE INDEX idx_leagues_external_id ON leagues(external_id);
```

#### 3.1.3 Teams Table

```sql
-- Football teams/clubs
CREATE TABLE teams (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- External reference
    external_id VARCHAR(100) UNIQUE,
    source VARCHAR(50),

    -- Basic info
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    acronym VARCHAR(10), -- MUN, LIV, etc.
    country VARCHAR(100),
    country_code VARCHAR(3),

    -- Media
    logo_url VARCHAR(500),
    cover_url VARCHAR(500),

    -- Details
    founded_year INT,
    stadium VARCHAR(255),
    stadium_capacity INT,
    city VARCHAR(100),

    -- Colors
    primary_color VARCHAR(7), -- Hex color #FFFFFF
    secondary_color VARCHAR(7),

    -- Metadata
    website_url VARCHAR(500),
    is_national_team BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_teams_name ON teams(name);
CREATE INDEX idx_teams_country ON teams(country);
CREATE INDEX idx_teams_external_id ON teams(external_id);
```

#### 3.1.4 Fixtures Table

```sql
-- Match fixtures/schedule
CREATE TABLE fixtures (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- External reference
    external_id VARCHAR(100) UNIQUE,
    source VARCHAR(50),

    -- Relations
    league_id UUID REFERENCES leagues(id) ON DELETE CASCADE,
    home_team_id UUID REFERENCES teams(id) ON DELETE CASCADE,
    away_team_id UUID REFERENCES teams(id) ON DELETE CASCADE,

    -- Match info
    match_date TIMESTAMP NOT NULL,
    venue VARCHAR(255),
    round VARCHAR(50), -- "Matchday 15", "Quarter-final"
    group_name VARCHAR(10), -- "Group A" for tournaments

    -- Status
    status VARCHAR(50) DEFAULT 'scheduled',
    -- Possible values: 'scheduled', 'live', 'halftime', 'finished',
    --                  'postponed', 'cancelled', 'abandoned'

    -- Referee
    referee VARCHAR(255),

    -- Attendance
    attendance INT,

    -- Weather (if available)
    weather_condition VARCHAR(50),
    temperature DECIMAL(4,1),

    -- Metadata
    is_featured BOOLEAN DEFAULT FALSE,
    importance_score INT DEFAULT 0, -- Algorithm-based importance

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_fixtures_league_date ON fixtures(league_id, match_date DESC);
CREATE INDEX idx_fixtures_home_team ON fixtures(home_team_id, match_date DESC);
CREATE INDEX idx_fixtures_away_team ON fixtures(away_team_id, match_date DESC);
CREATE INDEX idx_fixtures_status ON fixtures(status);
CREATE INDEX idx_fixtures_match_date ON fixtures(match_date DESC);
CREATE INDEX idx_fixtures_live ON fixtures(status, match_date) WHERE status = 'live';

-- Composite index for team fixtures
CREATE INDEX idx_fixtures_teams ON fixtures(home_team_id, away_team_id, match_date);

-- Unique constraint
ALTER TABLE fixtures ADD CONSTRAINT uix_fixture
    UNIQUE(league_id, home_team_id, away_team_id, match_date);
```

#### 3.1.5 User Favorites Table

```sql
-- User favorite teams/leagues
CREATE TABLE user_favorites (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relations
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Polymorphic relation
    entity_type VARCHAR(20) NOT NULL, -- 'team' or 'league'
    entity_id UUID NOT NULL,

    -- Metadata
    notification_enabled BOOLEAN DEFAULT TRUE,
    added_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_entity_type CHECK (entity_type IN ('team', 'league')),
    CONSTRAINT uix_user_favorite UNIQUE(user_id, entity_type, entity_id)
);

-- Indexes
CREATE INDEX idx_user_favorites_user ON user_favorites(user_id);
CREATE INDEX idx_user_favorites_entity ON user_favorites(entity_type, entity_id);
```

#### 3.1.6 Crawl Jobs Table

```sql
-- Track crawling job status
CREATE TABLE crawl_jobs (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Job info
    job_type VARCHAR(100) NOT NULL,
    -- Values: 'live_scores', 'fixtures', 'league_tables', 'team_stats', 'player_stats'

    source VARCHAR(100) NOT NULL, -- 'flashscore', 'livescore', etc.

    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    -- Values: 'pending', 'running', 'success', 'failed', 'timeout'

    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms INT, -- Duration in milliseconds

    -- Results
    items_crawled INT DEFAULT 0,
    items_updated INT DEFAULT 0,
    items_failed INT DEFAULT 0,

    -- Error handling
    error_message TEXT,
    error_traceback TEXT,
    retry_count INT DEFAULT 0,

    -- Metadata
    celery_task_id VARCHAR(255), -- Celery task UUID
    worker_name VARCHAR(100),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_crawl_jobs_status ON crawl_jobs(status, created_at DESC);
CREATE INDEX idx_crawl_jobs_type ON crawl_jobs(job_type, created_at DESC);
CREATE INDEX idx_crawl_jobs_created ON crawl_jobs(created_at DESC);
CREATE INDEX idx_crawl_jobs_celery ON crawl_jobs(celery_task_id);
```

#### 3.1.7 API Keys Table (Future)

```sql
-- API keys for external integrations
CREATE TABLE api_keys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Key
    key_hash VARCHAR(255) UNIQUE NOT NULL, -- Hashed API key
    key_prefix VARCHAR(20) NOT NULL, -- First few chars for identification

    -- Metadata
    name VARCHAR(100),
    description TEXT,

    -- Permissions
    scopes TEXT[], -- Array of allowed scopes
    rate_limit_per_hour INT DEFAULT 1000,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    expires_at TIMESTAMP,

    -- Usage tracking
    last_used_at TIMESTAMP,
    request_count INT DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_api_keys_user ON api_keys(user_id);
CREATE INDEX idx_api_keys_active ON api_keys(is_active) WHERE is_active = TRUE;
```

### 3.2 MongoDB Collections (Flexible Schema)

#### 3.2.1 Matches Collection

```javascript
// matches collection
{
  _id: ObjectId("..."),

  // External reference
  external_id: "match_flashscore_12345",
  source: "flashscore",
  fixture_id: "uuid-from-postgresql", // Reference to fixtures table

  // League info
  league: {
    id: "uuid",
    name: "Premier League",
    country: "England",
    logo: "https://..."
  },

  // Teams
  home_team: {
    id: "uuid",
    name: "Manchester United",
    short_name: "MUN",
    logo: "https://..."
  },
  away_team: {
    id: "uuid",
    name: "Liverpool",
    short_name: "LIV",
    logo: "https://..."
  },

  // Match timing
  match_date: ISODate("2024-11-08T15:00:00Z"),
  kickoff_time: ISODate("2024-11-08T15:00:00Z"),

  // Status
  status: "live", // scheduled, live, halftime, finished, postponed, cancelled
  minute: 67,
  added_time: 3, // Stoppage time
  period: "second_half", // first_half, halftime, second_half, extra_time, penalties

  // Score
  score: {
    home: 2,
    away: 1,
    halftime: { home: 1, away: 0 },
    fulltime: { home: null, away: null }, // null if not finished
    extra_time: { home: null, away: null },
    penalty: { home: null, away: null }
  },

  // Events timeline
  events: [
    {
      id: "evt_1",
      type: "goal",
      minute: 23,
      added_time: 0,
      player: {
        id: "player_uuid",
        name: "Marcus Rashford"
      },
      team: "home",
      assist: {
        id: "player_uuid",
        name: "Bruno Fernandes"
      },
      goal_type: "regular", // regular, penalty, own_goal, free_kick
      body_part: "right_foot", // left_foot, right_foot, head
      description: "Right foot shot from center of box to bottom right corner"
    },
    {
      id: "evt_2",
      type: "yellow_card",
      minute: 45,
      added_time: 2,
      player: {
        id: "player_uuid",
        name: "Casemiro"
      },
      team: "home",
      reason: "Foul"
    },
    {
      id: "evt_3",
      type: "substitution",
      minute: 60,
      player_out: {
        id: "player_uuid",
        name: "Marcus Rashford"
      },
      player_in: {
        id: "player_uuid",
        name: "Antony"
      },
      team: "home"
    }
    // Other event types: red_card, penalty_missed, var_decision
  ],

  // Match statistics
  statistics: {
    possession: { home: 55, away: 45 },
    shots: { home: 12, away: 8 },
    shots_on_target: { home: 5, away: 3 },
    shots_off_target: { home: 4, away: 3 },
    shots_blocked: { home: 3, away: 2 },
    corners: { home: 6, away: 4 },
    offsides: { home: 2, away: 1 },
    fouls: { home: 10, away: 12 },
    yellow_cards: { home: 2, away: 1 },
    red_cards: { home: 0, away: 0 },
    passes: { home: 456, away: 398 },
    pass_accuracy: { home: 85.2, away: 78.5 },
    tackles: { home: 18, away: 22 },
    saves: { home: 2, away: 3 }
  },

  // Lineups
  lineups: {
    home: {
      formation: "4-2-3-1",
      starting_eleven: [
        {
          player_id: "uuid",
          name: "David de Gea",
          shirt_number: 1,
          position: "GK",
          position_x: 5,
          position_y: 50
        }
        // ... 10 more players
      ],
      substitutes: [
        {
          player_id: "uuid",
          name: "Tom Heaton",
          shirt_number: 22,
          position: "GK"
        }
        // ... more substitutes
      ],
      coach: {
        name: "Erik ten Hag",
        country: "Netherlands"
      }
    },
    away: {
      // Similar structure
    }
  },

  // Head to head stats (optional)
  h2h_stats: {
    total_matches: 235,
    home_wins: 81,
    away_wins: 69,
    draws: 85,
    last_5_results: ["H", "A", "D", "H", "A"] // H=home win, A=away win, D=draw
  },

  // Venue
  venue: {
    name: "Old Trafford",
    city: "Manchester",
    country: "England",
    capacity: 74879,
    attendance: 73542
  },

  // Officials
  officials: {
    referee: "Michael Oliver",
    assistants: ["Stuart Burt", "Simon Bennett"],
    fourth_official: "Andy Madley",
    var: "Chris Kavanagh"
  },

  // Weather
  weather: {
    condition: "Partly cloudy",
    temperature: 12.5,
    humidity: 68,
    wind_speed: 15
  },

  // Metadata
  crawled_at: ISODate("2024-11-08T16:07:00Z"),
  crawl_source: "flashscore",
  data_quality_score: 95, // 0-100

  // Timestamps
  created_at: ISODate("2024-11-08T14:00:00Z"),
  updated_at: ISODate("2024-11-08T16:07:00Z")
}
```

**Indexes for matches collection:**

```javascript
// Primary indexes
db.matches.createIndex({ "external_id": 1 }, { unique: true });
db.matches.createIndex({ "fixture_id": 1 });

// Query optimization indexes
db.matches.createIndex({ "status": 1, "match_date": -1 });
db.matches.createIndex({ "league.id": 1, "match_date": -1 });
db.matches.createIndex({ "home_team.id": 1, "match_date": -1 });
db.matches.createIndex({ "away_team.id": 1, "match_date": -1 });
db.matches.createIndex({ "match_date": -1 });

// Live matches index (frequently queried)
db.matches.createIndex(
  { "status": 1, "match_date": -1 },
  {
    partialFilterExpression: { status: "live" },
    name: "idx_live_matches"
  }
);

// Compound index for team matches
db.matches.createIndex({
  "home_team.id": 1,
  "away_team.id": 1,
  "match_date": -1
});

// Text search index
db.matches.createIndex({
  "home_team.name": "text",
  "away_team.name": "text",
  "league.name": "text"
});
```

#### 3.2.2 League Tables Collection

```javascript
// league_tables collection
{
  _id: ObjectId("..."),

  // Reference
  league_id: "uuid-from-postgresql",
  season: "2024/2025",

  // League info
  league: {
    name: "Premier League",
    country: "England",
    logo: "https://..."
  },

  // Standings
  standings: [
    {
      position: 1,
      previous_position: 2, // Position in previous update
      movement: "up", // up, down, same

      // Team info
      team_id: "uuid",
      team_name: "Manchester City",
      team_logo: "https://...",

      // Record
      played: 11,
      won: 9,
      drawn: 1,
      lost: 1,

      // Goals
      goals_for: 28,
      goals_against: 10,
      goal_difference: 18,

      // Points
      points: 28,
      points_per_game: 2.55,

      // Form (last 5 matches)
      form: ["W", "W", "D", "W", "W"], // W=win, D=draw, L=loss

      // Home/Away split
      home_record: {
        played: 6,
        won: 5,
        drawn: 1,
        lost: 0,
        goals_for: 15,
        goals_against: 5
      },
      away_record: {
        played: 5,
        won: 4,
        drawn: 0,
        lost: 1,
        goals_for: 13,
        goals_against: 5
      },

      // Streaks
      current_streak: {
        type: "win",
        count: 3
      },

      // Qualification/Relegation zone
      zone: "champions_league",
      // Possible: champions_league, europa_league, conference_league,
      //           relegation, none
      zone_color: "#00ff00"
    }
    // ... 19 more teams
  ],

  // Last updated
  updated_at: ISODate("2024-11-08T10:00:00Z"),
  source: "flashscore",

  // Metadata
  created_at: ISODate("2024-08-01T00:00:00Z")
}
```

**Indexes for league_tables:**

```javascript
db.league_tables.createIndex(
  { "league_id": 1, "season": 1 },
  { unique: true }
);
db.league_tables.createIndex({ "updated_at": -1 });
```

#### 3.2.3 Player Statistics Collection

```javascript
// player_stats collection
{
  _id: ObjectId("..."),

  // Player info
  player_id: "uuid-from-future-players-table",
  player_name: "Erling Haaland",
  player_photo: "https://...",

  // Team
  team_id: "uuid",
  team_name: "Manchester City",
  team_logo: "https://...",

  // League & Season
  league_id: "uuid",
  league_name: "Premier League",
  season: "2024/2025",

  // Position
  position: "Forward",
  position_short: "FW",
  shirt_number: 9,

  // Appearance stats
  appearances: {
    total: 11,
    starting: 10,
    substitute: 1,
    minutes_played: 950,
    minutes_per_game: 86.4
  },

  // Scoring stats
  goals: {
    total: 15,
    left_foot: 5,
    right_foot: 7,
    header: 3,
    penalty: 2,
    free_kick: 0,
    inside_box: 13,
    outside_box: 2,
    goals_per_game: 1.36,
    minutes_per_goal: 63.3
  },

  // Assist stats
  assists: {
    total: 3,
    key_passes: 12,
    assists_per_game: 0.27
  },

  // Shooting stats
  shots: {
    total: 54,
    on_target: 32,
    off_target: 15,
    blocked: 7,
    accuracy_percentage: 59.3,
    shots_per_game: 4.9,
    conversion_rate: 27.8
  },

  // Passing stats
  passing: {
    total_passes: 285,
    completed: 224,
    accuracy_percentage: 78.6,
    key_passes: 12,
    passes_per_game: 25.9,
    long_balls: 23,
    crosses: 8
  },

  // Defensive stats
  defending: {
    tackles: 5,
    interceptions: 3,
    clearances: 2,
    blocks: 1,
    duels_won: 45,
    duels_total: 78,
    duel_success_rate: 57.7
  },

  // Discipline
  discipline: {
    yellow_cards: 1,
    red_cards: 0,
    fouls_committed: 8,
    fouls_suffered: 15
  },

  // Other stats
  other: {
    offsides: 12,
    successful_dribbles: 23,
    dribbles_attempted: 35,
    dribble_success_rate: 65.7
  },

  // Ratings
  average_rating: 8.2,
  highest_rating: 9.5,
  lowest_rating: 6.8,

  // Last updated
  updated_at: ISODate("2024-11-08T10:00:00Z"),
  source: "sofascore",

  created_at: ISODate("2024-08-01T00:00:00Z")
}
```

**Indexes for player_stats:**

```javascript
db.player_stats.createIndex({
  "player_id": 1,
  "season": 1,
  "league_id": 1
}, { unique: true });

db.player_stats.createIndex({ "team_id": 1, "season": 1 });
db.player_stats.createIndex({ "league_id": 1, "season": 1 });
db.player_stats.createIndex({ "goals.total": -1 }); // Top scorers
db.player_stats.createIndex({ "assists.total": -1 }); // Top assisters
```

#### 3.2.4 News/Articles Collection (Future)

```javascript
// news collection
{
  _id: ObjectId("..."),

  // Content
  title: "Manchester United wins 2-1 against Liverpool",
  slug: "manchester-united-wins-2-1-against-liverpool",
  summary: "Brief summary...",
  content: "Full article content...",

  // Relations
  match_id: "match_objectid",
  related_teams: ["team_uuid_1", "team_uuid_2"],
  related_players: ["player_uuid_1"],
  league_id: "league_uuid",

  // Media
  featured_image: "https://...",
  images: ["https://...", "https://..."],
  video_url: "https://...",

  // Metadata
  author: "John Doe",
  source: "ESPN",
  source_url: "https://...",
  category: "match_report", // match_report, transfer_news, injury, etc.
  tags: ["Premier League", "Manchester United", "Liverpool"],

  // Engagement
  views: 1523,
  likes: 45,
  shares: 12,

  // Timestamps
  published_at: ISODate("2024-11-08T17:00:00Z"),
  created_at: ISODate("2024-11-08T17:00:00Z"),
  updated_at: ISODate("2024-11-08T17:00:00Z")
}
```

### 3.3 Redis Data Structures

#### 3.3.1 Cache Keys

```
# Match data cache
cache:match:{match_id}                 # Match details (TTL: 30s for live, 1h for finished)
cache:matches:live                      # All live matches (TTL: 30s)
cache:matches:today                     # Today's matches (TTL: 5min)
cache:matches:upcoming                  # Upcoming matches (TTL: 1h)

# League data cache
cache:league:{league_id}                # League details (TTL: 1h)
cache:league:{league_id}:table          # League table (TTL: 1h)
cache:league:{league_id}:fixtures       # League fixtures (TTL: 1h)
cache:league:{league_id}:topscorers     # Top scorers (TTL: 1h)

# Team data cache
cache:team:{team_id}                    # Team details (TTL: 1h)
cache:team:{team_id}:fixtures           # Team fixtures (TTL: 30min)
cache:team:{team_id}:stats              # Team stats (TTL: 1h)

# User data cache
cache:user:{user_id}                    # User profile (TTL: 15min)
cache:user:{user_id}:favorites          # User favorites (TTL: 15min)

# API response cache
cache:api:{endpoint}:{params_hash}      # Generic API cache (TTL: varies)
```

#### 3.3.2 Session Storage

```
# User sessions
session:{session_id}                    # Session data (TTL: 7 days)

# WebSocket connections
ws:connection:{connection_id}           # Connection metadata
ws:user:{user_id}:connections           # Set of user's connections
```

#### 3.3.3 Pub/Sub Channels

```
# Real-time match updates
channel:match:{match_id}                # Updates for specific match
channel:league:{league_id}              # Updates for league matches
channel:team:{team_id}                  # Updates for team matches
channel:live:all                        # All live match updates

# System notifications
channel:system:broadcast                # System-wide notifications
channel:user:{user_id}                  # User-specific notifications
```

#### 3.3.4 Rate Limiting

```
# API rate limiting
ratelimit:ip:{ip_address}:{endpoint}    # Requests per IP (TTL: 1min)
ratelimit:user:{user_id}:{endpoint}     # Requests per user (TTL: 1min)
ratelimit:apikey:{key}                  # Requests per API key (TTL: 1min)

# Crawler rate limiting
crawler:ratelimit:{domain}              # Requests per domain (TTL: 1min)
```

#### 3.3.5 Celery Queues

```
# Task queues
celery:task:{task_id}                   # Task metadata
celery:result:{task_id}                 # Task result (TTL: 1h)

# Task scheduling
celery:beat:schedule                    # Beat scheduler
```

---

## 4. BACKEND API DESIGN

### 4.1 API Endpoints Specification

#### 4.1.1 Authentication Endpoints

```python
# POST /api/v1/auth/register
# Register new user

Request:
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePassword123!"
}

Response: 201 Created
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "is_premium": false,
  "created_at": "2024-11-08T10:00:00Z"
}

Errors:
- 400: Email already registered
- 400: Username already taken
- 422: Validation error (weak password, invalid email)
```

```python
# POST /api/v1/auth/login
# Login with username/email and password

Request (Form Data):
{
  "username": "johndoe",  # or email
  "password": "SecurePassword123!"
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

Errors:
- 401: Incorrect username or password
- 403: Inactive user
```

```python
# GET /api/v1/auth/me
# Get current user info (requires authentication)

Headers:
Authorization: Bearer {access_token}

Response: 200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "is_active": true,
  "is_premium": false,
  "created_at": "2024-11-08T10:00:00Z"
}

Errors:
- 401: Invalid or expired token
- 403: Inactive user
```

```python
# POST /api/v1/auth/refresh
# Refresh access token using refresh token

Request:
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}

Errors:
- 401: Invalid or expired refresh token
```

```python
# POST /api/v1/auth/logout
# Logout (client should discard tokens)

Headers:
Authorization: Bearer {access_token}

Response: 200 OK
{
  "message": "Successfully logged out"
}
```

#### 4.1.2 Matches Endpoints

```python
# GET /api/v1/matches/live
# Get all live matches

Query Parameters:
- limit: int (default=50, max=100)
- league_id: UUID (optional)

Response: 200 OK
[
  {
    "_id": "match_id",
    "home_team": {
      "id": "uuid",
      "name": "Manchester United",
      "short_name": "MUN",
      "logo": "https://..."
    },
    "away_team": {
      "id": "uuid",
      "name": "Liverpool",
      "short_name": "LIV",
      "logo": "https://..."
    },
    "league": {
      "id": "uuid",
      "name": "Premier League",
      "country": "England",
      "logo": "https://..."
    },
    "match_date": "2024-11-08T15:00:00Z",
    "status": "live",
    "minute": 67,
    "score": {
      "home": 2,
      "away": 1,
      "halftime": { "home": 1, "away": 0 }
    },
    "updated_at": "2024-11-08T16:07:00Z"
  }
]
```

```python
# GET /api/v1/matches/today
# Get today's matches (all statuses)

Query Parameters:
- limit: int (default=100, max=200)
- league_id: UUID (optional)
- status: str (optional) - 'scheduled', 'live', 'finished'

Response: 200 OK
[
  {
    "_id": "match_id",
    "home_team": {...},
    "away_team": {...},
    "league": {...},
    "match_date": "2024-11-08T20:00:00Z",
    "status": "scheduled",
    "score": {
      "home": 0,
      "away": 0
    }
  }
]
```

```python
# GET /api/v1/matches/upcoming
# Get upcoming matches (next N days)

Query Parameters:
- days: int (default=7, max=30)
- limit: int (default=100, max=200)
- league_id: UUID (optional)

Response: 200 OK
[...]
```

```python
# GET /api/v1/matches/{match_id}
# Get detailed match information

Response: 200 OK
{
  "_id": "match_id",
  "external_id": "flashscore_12345",
  "fixture_id": "uuid",
  "league": {...},
  "home_team": {...},
  "away_team": {...},
  "match_date": "2024-11-08T15:00:00Z",
  "status": "live",
  "minute": 67,
  "added_time": 3,
  "score": {
    "home": 2,
    "away": 1,
    "halftime": { "home": 1, "away": 0 }
  },
  "events": [
    {
      "type": "goal",
      "minute": 23,
      "player": "Marcus Rashford",
      "team": "home",
      "assist": "Bruno Fernandes",
      "description": "Right foot shot..."
    }
  ],
  "statistics": {
    "possession": { "home": 55, "away": 45 },
    "shots": { "home": 12, "away": 8 },
    "shots_on_target": { "home": 5, "away": 3 },
    "corners": { "home": 6, "away": 4 },
    "fouls": { "home": 10, "away": 12 }
  },
  "lineups": {
    "home": {
      "formation": "4-2-3-1",
      "starting_eleven": [...]
    },
    "away": {...}
  },
  "venue": {
    "name": "Old Trafford",
    "city": "Manchester"
  },
  "officials": {
    "referee": "Michael Oliver"
  },
  "updated_at": "2024-11-08T16:07:00Z"
}

Errors:
- 404: Match not found
```

```python
# GET /api/v1/matches/{match_id}/events
# Get match events timeline

Response: 200 OK
{
  "match_id": "match_id",
  "events": [
    {
      "id": "evt_1",
      "type": "goal",
      "minute": 23,
      "added_time": 0,
      "player": {
        "id": "uuid",
        "name": "Marcus Rashford"
      },
      "team": "home",
      "assist": {
        "id": "uuid",
        "name": "Bruno Fernandes"
      },
      "description": "..."
    }
  ]
}
```

```python
# GET /api/v1/matches/{match_id}/stats
# Get match statistics

Response: 200 OK
{
  "match_id": "match_id",
  "statistics": {
    "possession": { "home": 55, "away": 45 },
    "shots": { "home": 12, "away": 8 },
    "shots_on_target": { "home": 5, "away": 3 },
    "shots_off_target": { "home": 4, "away": 3 },
    "shots_blocked": { "home": 3, "away": 2 },
    "corners": { "home": 6, "away": 4 },
    "offsides": { "home": 2, "away": 1 },
    "fouls": { "home": 10, "away": 12 },
    "yellow_cards": { "home": 2, "away": 1 },
    "red_cards": { "home": 0, "away": 0 },
    "passes": { "home": 456, "away": 398 },
    "pass_accuracy": { "home": 85.2, "away": 78.5 }
  }
}
```

```python
# GET /api/v1/matches/{match_id}/lineups
# Get team lineups

Response: 200 OK
{
  "match_id": "match_id",
  "home": {
    "formation": "4-2-3-1",
    "starting_eleven": [
      {
        "player_id": "uuid",
        "name": "David de Gea",
        "shirt_number": 1,
        "position": "GK"
      }
    ],
    "substitutes": [...],
    "coach": {
      "name": "Erik ten Hag"
    }
  },
  "away": {...}
}
```

#### 4.1.3 Leagues Endpoints

```python
# GET /api/v1/leagues
# Get all leagues

Query Parameters:
- skip: int (default=0)
- limit: int (default=50, max=100)
- country: str (optional)
- is_featured: bool (optional)

Response: 200 OK
[
  {
    "id": "uuid",
    "name": "Premier League",
    "short_name": "EPL",
    "country": "England",
    "country_code": "ENG",
    "logo_url": "https://...",
    "season": "2024/2025",
    "is_featured": true,
    "priority": 10
  }
]
```

```python
# GET /api/v1/leagues/{league_id}
# Get league details

Response: 200 OK
{
  "id": "uuid",
  "name": "Premier League",
  "short_name": "EPL",
  "country": "England",
  "country_code": "ENG",
  "logo_url": "https://...",
  "banner_url": "https://...",
  "season": "2024/2025",
  "start_date": "2024-08-16",
  "end_date": "2025-05-18",
  "num_teams": 20,
  "is_active": true
}

Errors:
- 404: League not found
```

```python
# GET /api/v1/leagues/{league_id}/table
# Get league standings/table

Response: 200 OK
{
  "league_id": "uuid",
  "league": {
    "name": "Premier League",
    "country": "England",
    "logo": "https://..."
  },
  "season": "2024/2025",
  "standings": [
    {
      "position": 1,
      "previous_position": 2,
      "movement": "up",
      "team_id": "uuid",
      "team_name": "Manchester City",
      "team_logo": "https://...",
      "played": 11,
      "won": 9,
      "drawn": 1,
      "lost": 1,
      "goals_for": 28,
      "goals_against": 10,
      "goal_difference": 18,
      "points": 28,
      "form": ["W", "W", "D", "W", "W"],
      "zone": "champions_league"
    }
  ],
  "updated_at": "2024-11-08T10:00:00Z"
}

Errors:
- 404: League not found
- 404: Table not available yet
```

```python
# GET /api/v1/leagues/{league_id}/fixtures
# Get league fixtures

Query Parameters:
- status: str (optional) - 'scheduled', 'live', 'finished'
- limit: int (default=50, max=100)
- date_from: date (optional)
- date_to: date (optional)

Response: 200 OK
[
  {
    "fixture_id": "uuid",
    "match_id": "match_objectid",
    "home_team": {...},
    "away_team": {...},
    "match_date": "2024-11-09T15:00:00Z",
    "status": "scheduled",
    "round": "Matchday 12",
    "venue": "Emirates Stadium"
  }
]
```

```python
# GET /api/v1/leagues/{league_id}/topscorers
# Get league top scorers

Query Parameters:
- limit: int (default=20, max=50)
- season: str (optional, default=current)

Response: 200 OK
[
  {
    "position": 1,
    "player_id": "uuid",
    "player_name": "Erling Haaland",
    "player_photo": "https://...",
    "team_id": "uuid",
    "team_name": "Manchester City",
    "team_logo": "https://...",
    "goals": 15,
    "assists": 3,
    "matches_played": 11,
    "goals_per_game": 1.36
  }
]
```

#### 4.1.4 Teams Endpoints

```python
# GET /api/v1/teams/{team_id}
# Get team details

Response: 200 OK
{
  "id": "uuid",
  "name": "Manchester United",
  "short_name": "Man United",
  "acronym": "MUN",
  "country": "England",
  "logo_url": "https://...",
  "cover_url": "https://...",
  "founded_year": 1878,
  "stadium": "Old Trafford",
  "stadium_capacity": 74879,
  "city": "Manchester",
  "website_url": "https://..."
}

Errors:
- 404: Team not found
```

```python
# GET /api/v1/teams/{team_id}/fixtures
# Get team fixtures (past and upcoming)

Query Parameters:
- limit: int (default=20, max=50)
- status: str (optional)
- date_from: date (optional)
- date_to: date (optional)

Response: 200 OK
[
  {
    "match_id": "match_objectid",
    "fixture_id": "uuid",
    "league": {...},
    "home_team": {...},
    "away_team": {...},
    "match_date": "2024-11-08T15:00:00Z",
    "status": "finished",
    "score": {
      "home": 2,
      "away": 1
    },
    "is_home": true  # True if requested team is home
  }
]
```

```python
# GET /api/v1/teams/{team_id}/stats
# Get team statistics for current season

Query Parameters:
- season: str (optional, default=current)
- league_id: UUID (optional)

Response: 200 OK
{
  "team_id": "uuid",
  "team_name": "Manchester United",
  "season": "2024/2025",
  "overall": {
    "matches_played": 11,
    "won": 7,
    "drawn": 2,
    "lost": 2,
    "goals_for": 18,
    "goals_against": 10,
    "goal_difference": 8,
    "points": 23,
    "clean_sheets": 4
  },
  "home": {...},
  "away": {...},
  "form": ["W", "L", "W", "D", "W"]
}
```

```python
# GET /api/v1/teams/{team_id}/squad
# Get team squad/players

Response: 200 OK
{
  "team_id": "uuid",
  "team_name": "Manchester United",
  "season": "2024/2025",
  "players": [
    {
      "player_id": "uuid",
      "name": "Bruno Fernandes",
      "photo": "https://...",
      "position": "Midfielder",
      "shirt_number": 8,
      "nationality": "Portugal",
      "age": 29,
      "stats": {
        "appearances": 11,
        "goals": 3,
        "assists": 5
      }
    }
  ],
  "coaching_staff": [
    {
      "name": "Erik ten Hag",
      "role": "Manager",
      "nationality": "Netherlands"
    }
  ]
}
```

#### 4.1.5 User Endpoints

```python
# GET /api/v1/users/favorites
# Get user's favorite teams and leagues (requires auth)

Headers:
Authorization: Bearer {access_token}

Response: 200 OK
{
  "teams": [
    {
      "id": "favorite_uuid",
      "team_id": "team_uuid",
      "team_name": "Manchester United",
      "team_logo": "https://...",
      "notification_enabled": true,
      "added_at": "2024-11-01T10:00:00Z"
    }
  ],
  "leagues": [
    {
      "id": "favorite_uuid",
      "league_id": "league_uuid",
      "league_name": "Premier League",
      "league_logo": "https://...",
      "notification_enabled": true,
      "added_at": "2024-11-01T10:00:00Z"
    }
  ]
}
```

```python
# POST /api/v1/users/favorites
# Add favorite team or league (requires auth)

Headers:
Authorization: Bearer {access_token}

Request:
{
  "entity_type": "team",  # or "league"
  "entity_id": "uuid"
}

Response: 201 Created
{
  "id": "favorite_uuid",
  "entity_type": "team",
  "entity_id": "uuid"
}

Errors:
- 400: Invalid entity_type (must be 'team' or 'league')
- 400: Already in favorites
- 404: Entity not found
```

```python
# DELETE /api/v1/users/favorites/{favorite_id}
# Remove favorite (requires auth)

Headers:
Authorization: Bearer {access_token}

Response: 200 OK
{
  "message": "Favorite removed"
}

Errors:
- 404: Favorite not found
```

```python
# PATCH /api/v1/users/me
# Update user profile (requires auth)

Headers:
Authorization: Bearer {access_token}

Request:
{
  "full_name": "John Doe",
  "timezone": "America/New_York",
  "language": "en"
}

Response: 200 OK
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "timezone": "America/New_York",
  "language": "en"
}
```

#### 4.1.6 Admin Endpoints (Future)

```python
# POST /api/v1/admin/crawl/trigger
# Manually trigger crawl job (requires admin)

Headers:
Authorization: Bearer {admin_token}

Request:
{
  "job_type": "live_scores",  # or "fixtures", "league_tables"
  "source": "flashscore",     # optional
  "league_id": "uuid"         # optional
}

Response: 202 Accepted
{
  "job_id": "uuid",
  "status": "pending",
  "message": "Crawl job queued"
}
```

```python
# GET /api/v1/admin/crawl/status
# Get crawl job status (requires admin)

Query Parameters:
- job_type: str (optional)
- status: str (optional)
- limit: int (default=50)

Response: 200 OK
[
  {
    "id": "uuid",
    "job_type": "live_scores",
    "source": "flashscore",
    "status": "success",
    "started_at": "2024-11-08T16:00:00Z",
    "completed_at": "2024-11-08T16:00:30Z",
    "duration_ms": 30000,
    "items_crawled": 25
  }
]
```

```python
# GET /api/v1/admin/crawl/logs
# Get crawl logs (requires admin)

Query Parameters:
- job_id: UUID
- limit: int (default=100)

Response: 200 OK
{
  "job_id": "uuid",
  "logs": [
    {
      "timestamp": "2024-11-08T16:00:05Z",
      "level": "INFO",
      "message": "Started crawling match 12345"
    }
  ]
}
```

### 4.2 WebSocket Protocol

#### 4.2.1 Connection

```javascript
// Client connects
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected');
};
```

#### 4.2.2 Client Messages

```javascript
// Subscribe to channels
ws.send(JSON.stringify({
  action: 'subscribe',
  channels: [
    'match:12345',           // Specific match
    'league:uuid',           // All matches in league
    'team:uuid',             // Team's matches
    'live:all'               // All live matches
  ]
}));

// Unsubscribe from channels
ws.send(JSON.stringify({
  action: 'unsubscribe',
  channels: ['match:12345']
}));

// Ping/heartbeat
ws.send(JSON.stringify({
  action: 'ping'
}));
```

#### 4.2.3 Server Messages

```javascript
// Match update (score change, minute update)
{
  type: 'match_update',
  channel: 'match:12345',
  timestamp: '2024-11-08T16:07:00Z',
  data: {
    match_id: '12345',
    minute: 68,
    score: {
      home: 2,
      away: 1
    },
    status: 'live'
  }
}

// Goal event
{
  type: 'goal',
  channel: 'match:12345',
  timestamp: '2024-11-08T16:07:00Z',
  data: {
    match_id: '12345',
    team: 'home',
    player: 'Marcus Rashford',
    minute: 68,
    score: {
      home: 2,
      away: 1
    }
  }
}

// Card event
{
  type: 'yellow_card',
  channel: 'match:12345',
  timestamp: '2024-11-08T16:08:00Z',
  data: {
    match_id: '12345',
    team: 'away',
    player: 'Virgil van Dijk',
    minute: 69
  }
}

// Match status change
{
  type: 'match_status',
  channel: 'match:12345',
  timestamp: '2024-11-08T15:45:00Z',
  data: {
    match_id: '12345',
    status: 'halftime',
    score: {
      home: 1,
      away: 0
    }
  }
}

// Subscription confirmation
{
  type: 'subscribed',
  channels: ['match:12345', 'live:all']
}

// Pong response
{
  type: 'pong'
}

// Error
{
  type: 'error',
  error: 'Invalid channel format',
  code: 'INVALID_CHANNEL'
}
```

### 4.3 Error Handling

#### 4.3.1 Error Response Format

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2024-11-08T16:00:00Z",
  "path": "/api/v1/matches/live",
  "trace_id": "uuid"
}
```

#### 4.3.2 HTTP Status Codes

```
200 OK - Success
201 Created - Resource created
202 Accepted - Request accepted (async processing)
204 No Content - Success with no response body

400 Bad Request - Invalid request data
401 Unauthorized - Authentication required
403 Forbidden - Insufficient permissions
404 Not Found - Resource not found
409 Conflict - Resource conflict (duplicate)
422 Unprocessable Entity - Validation error
429 Too Many Requests - Rate limit exceeded

500 Internal Server Error - Server error
502 Bad Gateway - Upstream service error
503 Service Unavailable - Service temporarily unavailable
504 Gateway Timeout - Upstream timeout
```

---

## 5. CRAWLING STRATEGY

### 5.1 Data Sources

#### 5.1.1 Primary Sources

```
1. FlashScore (flashscore.com)
   ├─ Coverage: Excellent (100+ leagues)
   ├─ Update Speed: Fast (10-30s delay)
   ├─ Data Quality: High
   ├─ Technology: JavaScript-rendered (Playwright required)
   ├─ Difficulty: Hard (anti-bot protection)
   └─ Best for: Live scores, detailed stats

2. LiveScore (livescore.com)
   ├─ Coverage: Good (major leagues)
   ├─ Update Speed: Very Fast (5-15s delay)
   ├─ Data Quality: Medium
   ├─ Technology: Static HTML (httpx sufficient)
   ├─ Difficulty: Medium
   └─ Best for: Quick live score updates

3. SofaScore API (api.sofascore.com)
   ├─ Coverage: Excellent
   ├─ Update Speed: Fast
   ├─ Data Quality: Very High (detailed stats)
   ├─ Technology: JSON API
   ├─ Difficulty: Easy (API-based)
   └─ Best for: Match statistics, player stats

4. ESPN Soccer (espn.com/soccer)
   ├─ Coverage: Good
   ├─ Data Quality: High
   ├─ Technology: Static HTML
   ├─ Difficulty: Easy
   └─ Best for: News, fixtures, tables
```

#### 5.1.2 Backup/Alternative Sources

```
- Football-Data.org API (free tier: 10 requests/min)
- API-Football (RapidAPI) (paid)
- TheSportsDB API (limited free tier)
- Sportradar API (enterprise, paid)
```

### 5.2 Crawling Tasks Schedule

```python
# Celery Beat Schedule
{
    # HIGH PRIORITY - Live matches
    'crawl-live-scores': {
        'task': 'tasks.live_scores.crawl_live_scores',
        'schedule': 30.0,  # Every 30 seconds
        'options': {
            'priority': 10,
            'expires': 25  # Expire task if not picked up in 25s
        }
    },

    # CRITICAL PRIORITY - Match events
    'crawl-match-events': {
        'task': 'tasks.live_scores.crawl_match_events',
        'schedule': 10.0,  # Every 10 seconds (for goals, cards)
        'options': {
            'priority': 10,
            'expires': 8
        }
    },

    # MEDIUM PRIORITY - Fixtures
    'crawl-daily-fixtures': {
        'task': 'tasks.fixtures.crawl_daily_fixtures',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        'options': {'priority': 5}
    },

    'crawl-hourly-fixtures': {
        'task': 'tasks.fixtures.crawl_upcoming_fixtures',
        'schedule': crontab(minute=0),  # Every hour
        'options': {'priority': 5}
    },

    # LOW PRIORITY - League tables
    'crawl-league-tables': {
        'task': 'tasks.stats.crawl_league_tables',
        'schedule': crontab(minute=0),  # Every hour
        'options': {'priority': 3}
    },

    # LOW PRIORITY - Team stats
    'update-team-stats': {
        'task': 'tasks.stats.update_team_stats',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        'options': {'priority': 2}
    },

    # LOW PRIORITY - Player stats
    'update-player-stats': {
        'task': 'tasks.stats.update_player_stats',
        'schedule': crontab(minute=0, hour=3),  # 3 AM daily
        'options': {'priority': 2}
    }
}
```

### 5.3 Crawling Implementation Details

#### 5.3.1 Live Score Crawling Flow

```python
# Step-by-step process

1. Get list of live matches from database
   └─ Query: matches.find({status: "live"})

2. For each live match:
   ├─ Check last update time
   ├─ If updated < 30s ago: skip (recent update)
   └─ If updated >= 30s ago: crawl

3. Crawl match data:
   ├─ Build URL from external_id
   ├─ Fetch HTML (Playwright if needed)
   ├─ Parse: score, minute, status
   └─ Handle errors (retry with backoff)

4. Compare with existing data:
   ├─ If score changed: Mark as "goal event"
   ├─ If minute changed: Update minute
   ├─ If status changed: Update status
   └─ If no changes: Skip database update

5. Update database:
   ├─ MongoDB: matches.update_one()
   └─ Redis: Invalidate cache

6. Broadcast updates:
   ├─ Redis Pub: "match:{id}"
   ├─ Redis Pub: "live:all"
   └─ WebSocket: Send to subscribers

7. Log results:
   ├─ Success: Log metrics
   └─ Failure: Log error + retry
```

#### 5.3.2 Anti-Detection Strategies

```python
# 1. User-Agent Rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',
    'Mozilla/5.0 (X11; Linux x86_64) ...',
    # ... 20+ user agents
]

# 2. Proxy Rotation (if using paid service)
PROXY_CONFIG = {
    'provider': 'scraperapi',  # or 'brightdata', 'smartproxy'
    'api_key': 'your_key',
    'rotation': 'per_request',
    'country': 'US'
}

# 3. Request Headers
HEADERS = {
    'User-Agent': random.choice(USER_AGENTS),
    'Accept': 'text/html,application/xhtml+xml,...',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://www.google.com/',
    'Cache-Control': 'max-age=0'
}

# 4. Rate Limiting per Domain
RATE_LIMITS = {
    'flashscore.com': {
        'requests_per_minute': 20,
        'concurrent_requests': 3,
        'download_delay': 2  # seconds between requests
    },
    'livescore.com': {
        'requests_per_minute': 30,
        'concurrent_requests': 5,
        'download_delay': 1
    }
}

# 5. Retry Strategy
RETRY_CONFIG = {
    'max_retries': 3,
    'backoff_factor': 2,  # 2s, 4s, 8s
    'retry_on': [429, 500, 502, 503, 504],
    'retry_exceptions': [TimeoutError, ConnectionError]
}

# 6. Playwright Stealth
# Use playwright-stealth to avoid detection
from playwright_stealth import stealth_sync

async def fetch_with_playwright(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York'
        )

        page = await context.new_page()

        # Apply stealth
        await stealth_async(page)

        await page.goto(url, wait_until='domcontentloaded')
        await page.wait_for_timeout(random.randint(1000, 3000))

        html = await page.content()

        await browser.close()

        return html
```

#### 5.3.3 Error Handling & Recovery

```python
# Error types and handling

1. Network Errors (TimeoutError, ConnectionError)
   └─ Action: Retry with exponential backoff
   └─ Max retries: 3
   └─ If still failing: Skip and log error

2. HTTP Errors (4xx, 5xx)
   ├─ 403 Forbidden: IP banned
   │   └─ Action: Switch proxy, increase delay
   ├─ 429 Too Many Requests: Rate limited
   │   └─ Action: Wait 60s, reduce request rate
   ├─ 500+ Server Error
   │   └─ Action: Retry after 30s
   └─ Other: Log and skip

3. Parsing Errors (Data not found, invalid format)
   └─ Action: Log HTML for debugging, try backup source

4. Database Errors (Connection, timeout)
   └─ Action: Retry connection, queue for later

5. Task Timeout (Celery soft/hard limit)
   └─ Action: Mark as failed, retry with lower batch size
```

#### 5.3.4 Data Validation

```python
# Validate crawled data before saving

def validate_match_data(data):
    """Validate match data structure and values"""

    errors = []

    # Required fields
    required = ['external_id', 'home_team', 'away_team', 'status']
    for field in required:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Score validation
    if 'score' in data:
        if not isinstance(data['score'].get('home'), int):
            errors.append("Invalid home score")
        if not isinstance(data['score'].get('away'), int):
            errors.append("Invalid away score")

        # Scores can't be negative
        if data['score'].get('home', 0) < 0:
            errors.append("Negative home score")
        if data['score'].get('away', 0) < 0:
            errors.append("Negative away score")

    # Status validation
    valid_statuses = ['scheduled', 'live', 'halftime', 'finished', 'postponed', 'cancelled']
    if data.get('status') not in valid_statuses:
        errors.append(f"Invalid status: {data.get('status')}")

    # Minute validation
    if 'minute' in data:
        minute = data['minute']
        if not isinstance(minute, int) or minute < 0 or minute > 120:
            errors.append(f"Invalid minute: {minute}")

    # Events validation
    if 'events' in data:
        for i, event in enumerate(data['events']):
            if 'type' not in event:
                errors.append(f"Event {i}: missing type")
            if 'minute' not in event:
                errors.append(f"Event {i}: missing minute")

    if errors:
        raise ValidationError(errors)

    return True
```

### 5.4 Crawler Implementation Examples

#### 5.4.1 FlashScore Crawler (Template)

```python
# crawlers/flashscore.py

from crawlers.base import BaseCrawler
from bs4 import BeautifulSoup
import structlog

logger = structlog.get_logger()


class FlashScoreCrawler(BaseCrawler):
    """
    FlashScore crawler implementation

    NOTE: This is a TEMPLATE. Selectors will change frequently.
    Production requires:
    - Regular selector updates
    - Proxy rotation
    - Anti-bot bypass
    - Error handling
    """

    BASE_URL = "https://www.flashscore.com"

    async def crawl_match(self, match_id: str):
        """
        Crawl single match from FlashScore

        Args:
            match_id: FlashScore match ID

        Returns:
            dict: Match data
        """
        url = f"{self.BASE_URL}/match/{match_id}/"

        try:
            # Use Playwright for JS-rendered content
            html = await self.fetch_html(url, use_playwright=True)

            if not html:
                logger.warning("no_html_content", url=url)
                return None

            soup = BeautifulSoup(html, 'lxml')

            # Parse data
            match_data = {
                'external_id': f"flashscore_{match_id}",
                'score': self._parse_score(soup),
                'minute': self._parse_minute(soup),
                'status': self._parse_status(soup),
                'events': self._parse_events(soup),
                'statistics': self._parse_statistics(soup)
            }

            # Validate
            self.validate_match_data(match_data)

            logger.info("match_crawled", match_id=match_id)

            return match_data

        except Exception as e:
            logger.error("crawl_match_failed", match_id=match_id, error=str(e))
            return None

    def _parse_score(self, soup: BeautifulSoup):
        """Parse score from HTML"""
        try:
            # TEMPLATE selectors - will need updating
            home_score_elem = soup.select_one('.detailScore__wrapper span:nth-child(1)')
            away_score_elem = soup.select_one('.detailScore__wrapper span:nth-child(3)')

            if home_score_elem and away_score_elem:
                return {
                    'home': int(home_score_elem.text.strip()),
                    'away': int(away_score_elem.text.strip())
                }
        except Exception as e:
            logger.error("parse_score_failed", error=str(e))

        return {'home': 0, 'away': 0}

    def _parse_minute(self, soup: BeautifulSoup):
        """Parse current minute"""
        try:
            minute_elem = soup.select_one('.detailScore__status')
            if minute_elem:
                text = minute_elem.text.strip()
                # Extract number from "67'"
                return int(text.replace("'", ""))
        except:
            pass

        return None

    def _parse_status(self, soup: BeautifulSoup):
        """Parse match status"""
        try:
            status_elem = soup.select_one('.detailScore__status')
            if status_elem:
                text = status_elem.text.strip().lower()

                if "'" in text or 'live' in text:
                    return 'live'
                elif 'finished' in text or 'ft' in text:
                    return 'finished'
                elif 'half' in text or 'ht' in text:
                    return 'halftime'
        except:
            pass

        return 'scheduled'

    def _parse_events(self, soup: BeautifulSoup):
        """Parse match events"""
        events = []

        try:
            # TEMPLATE selectors
            event_rows = soup.select('.smv__incident')

            for row in event_rows:
                event = self._parse_event_row(row)
                if event:
                    events.append(event)

        except Exception as e:
            logger.error("parse_events_failed", error=str(e))

        return events

    def _parse_event_row(self, row):
        """Parse single event row"""
        # TEMPLATE implementation
        return {
            'type': 'goal',
            'minute': 45,
            'player': 'Player Name',
            'team': 'home'
        }

    def _parse_statistics(self, soup: BeautifulSoup):
        """Parse match statistics"""
        # TEMPLATE implementation
        return {
            'possession': {'home': 50, 'away': 50},
            'shots': {'home': 0, 'away': 0}
        }
```

---

## 6. REAL-TIME IMPLEMENTATION

### 6.1 WebSocket Server Architecture

```python
# api/routes/websocket.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
import structlog

logger = structlog.get_logger()
router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections and channel subscriptions
    """

    def __init__(self):
        # Channel subscriptions
        # Format: {channel: {websocket1, websocket2, ...}}
        self.active_connections: Dict[str, Set[WebSocket]] = {}

        # Connection metadata
        # Format: {websocket: {user_id, connected_at, ...}}
        self.connection_metadata: Dict[WebSocket, dict] = {}

        # User connections (for authenticated users)
        # Format: {user_id: {websocket1, websocket2, ...}}
        self.user_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None):
        """Accept and register new connection"""
        await websocket.accept()

        # Store metadata
        self.connection_metadata[websocket] = {
            'user_id': user_id,
            'connected_at': datetime.utcnow(),
            'subscriptions': set()
        }

        # Track user connections (if authenticated)
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)

        logger.info(
            "websocket_connected",
            user_id=user_id,
            total_connections=len(self.connection_metadata)
        )

    def disconnect(self, websocket: WebSocket):
        """Remove connection from all channels"""
        # Get metadata
        metadata = self.connection_metadata.get(websocket, {})
        user_id = metadata.get('user_id')
        subscriptions = metadata.get('subscriptions', set())

        # Remove from all subscribed channels
        for channel in subscriptions:
            if channel in self.active_connections:
                self.active_connections[channel].discard(websocket)

                # Clean up empty channels
                if not self.active_connections[channel]:
                    del self.active_connections[channel]

        # Remove from user connections
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Remove metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]

        logger.info(
            "websocket_disconnected",
            user_id=user_id,
            total_connections=len(self.connection_metadata)
        )

    def subscribe(self, channel: str, websocket: WebSocket):
        """Subscribe connection to channel"""
        # Add to channel
        if channel not in self.active_connections:
            self.active_connections[channel] = set()
        self.active_connections[channel].add(websocket)

        # Update metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]['subscriptions'].add(channel)

        logger.info(
            "channel_subscribed",
            channel=channel,
            subscribers=len(self.active_connections[channel])
        )

    def unsubscribe(self, channel: str, websocket: WebSocket):
        """Unsubscribe connection from channel"""
        if channel in self.active_connections:
            self.active_connections[channel].discard(websocket)

            # Clean up empty channel
            if not self.active_connections[channel]:
                del self.active_connections[channel]

        # Update metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]['subscriptions'].discard(channel)

        logger.info("channel_unsubscribed", channel=channel)

    async def broadcast(self, channel: str, message: dict):
        """
        Broadcast message to all subscribers of a channel
        """
        if channel not in self.active_connections:
            return

        dead_connections = set()
        sent_count = 0

        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.error("websocket_send_failed", error=str(e))
                dead_connections.add(connection)

        # Clean up dead connections
        for conn in dead_connections:
            self.disconnect(conn)

        logger.debug(
            "message_broadcast",
            channel=channel,
            sent=sent_count,
            failed=len(dead_connections)
        )

    async def send_to_user(self, user_id: str, message: dict):
        """Send message to all connections of a specific user"""
        if user_id not in self.user_connections:
            return

        for connection in self.user_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("user_message_failed", user_id=user_id, error=str(e))

    def get_stats(self):
        """Get connection statistics"""
        return {
            'total_connections': len(self.connection_metadata),
            'total_channels': len(self.active_connections),
            'authenticated_users': len(self.user_connections),
            'channels': {
                channel: len(subscribers)
                for channel, subscribers in self.active_connections.items()
            }
        }


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates

    Client can subscribe to:
    - match:{match_id} - Updates for specific match
    - league:{league_id} - All matches in league
    - team:{team_id} - Team's matches
    - live:all - All live matches
    - user:{user_id} - User notifications (requires auth)
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            action = data.get('action')

            if action == 'subscribe':
                channels = data.get('channels', [])
                for channel in channels:
                    manager.subscribe(channel, websocket)

                await websocket.send_json({
                    'type': 'subscribed',
                    'channels': channels
                })

            elif action == 'unsubscribe':
                channels = data.get('channels', [])
                for channel in channels:
                    manager.unsubscribe(channel, websocket)

                await websocket.send_json({
                    'type': 'unsubscribed',
                    'channels': channels
                })

            elif action == 'ping':
                await websocket.send_json({'type': 'pong'})

            elif action == 'get_stats':
                # Admin only (add auth check)
                stats = manager.get_stats()
                await websocket.send_json({
                    'type': 'stats',
                    'data': stats
                })

            else:
                await websocket.send_json({
                    'type': 'error',
                    'error': 'Unknown action',
                    'code': 'UNKNOWN_ACTION'
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)

    except Exception as e:
        logger.error("websocket_error", error=str(e))
        manager.disconnect(websocket)


def get_connection_manager():
    """Get global connection manager instance"""
    return manager
```

### 6.2 Redis Pub/Sub Integration

```python
# services/notification_service.py

import redis.asyncio as redis
import json
from api.routes.websocket import get_connection_manager
import structlog

logger = structlog.get_logger()


class NotificationService:
    """
    Service for publishing real-time notifications
    """

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None

    async def init(self):
        """Initialize Redis connection"""
        self.redis_client = await redis.from_url(self.redis_url)

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()

    async def publish_match_update(self, match_id: str, data: dict):
        """
        Publish match update

        Args:
            match_id: Match ID
            data: Match data (score, minute, status)
        """
        message = {
            'type': 'match_update',
            'channel': f'match:{match_id}',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'match_id': match_id,
                **data
            }
        }

        # Publish to Redis
        await self.redis_client.publish(
            f'match:{match_id}',
            json.dumps(message)
        )

        # Also publish to "live:all" channel
        await self.redis_client.publish(
            'live:all',
            json.dumps(message)
        )

        logger.info("match_update_published", match_id=match_id)

    async def publish_goal_event(self, match_id: str, event: dict):
        """
        Publish goal event

        Args:
            match_id: Match ID
            event: Event data
        """
        message = {
            'type': 'goal',
            'channel': f'match:{match_id}',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'match_id': match_id,
                **event
            }
        }

        # Publish to multiple channels
        channels = [
            f'match:{match_id}',
            'live:all'
        ]

        # Add team channels if available
        if 'home_team_id' in event:
            channels.append(f"team:{event['home_team_id']}")
        if 'away_team_id' in event:
            channels.append(f"team:{event['away_team_id']}")

        # Publish to all channels
        for channel in channels:
            await self.redis_client.publish(channel, json.dumps(message))

        logger.info("goal_event_published", match_id=match_id)

    async def publish_card_event(self, match_id: str, event: dict):
        """Publish card event (yellow/red)"""
        message = {
            'type': event['type'],  # 'yellow_card' or 'red_card'
            'channel': f'match:{match_id}',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'match_id': match_id,
                **event
            }
        }

        await self.redis_client.publish(
            f'match:{match_id}',
            json.dumps(message)
        )

    async def publish_match_status(self, match_id: str, status: str, data: dict = None):
        """
        Publish match status change

        Args:
            match_id: Match ID
            status: New status (halftime, finished, etc.)
            data: Additional data
        """
        message = {
            'type': 'match_status',
            'channel': f'match:{match_id}',
            'timestamp': datetime.utcnow().isoformat(),
            'data': {
                'match_id': match_id,
                'status': status,
                **(data or {})
            }
        }

        await self.redis_client.publish(
            f'match:{match_id}',
            json.dumps(message)
        )

        await self.redis_client.publish(
            'live:all',
            json.dumps(message)
        )

        logger.info("match_status_published", match_id=match_id, status=status)


# Background task to listen to Redis and broadcast via WebSocket
async def redis_listener(redis_url: str):
    """
    Background task that listens to Redis pub/sub
    and broadcasts messages to WebSocket clients
    """
    redis_client = await redis.from_url(redis_url)
    pubsub = redis_client.pubsub()

    # Subscribe to all channels
    await pubsub.psubscribe('match:*', 'team:*', 'league:*', 'live:*')

    manager = get_connection_manager()

    logger.info("redis_listener_started")

    try:
        async for message in pubsub.listen():
            if message['type'] == 'pmessage':
                try:
                    # Parse message
                    data = json.loads(message['data'])
                    channel = data['channel']

                    # Broadcast to WebSocket subscribers
                    await manager.broadcast(channel, data)

                except Exception as e:
                    logger.error("redis_message_failed", error=str(e))

    finally:
        await pubsub.unsubscribe()
        await redis_client.close()
        logger.info("redis_listener_stopped")
```

### 6.3 Real-time Update Flow (Complete)

```
┌──────────────────────────────────────────────────────────┐
│ 1. CRAWLING (Every 30s for live matches)                │
├──────────────────────────────────────────────────────────┤
│ Celery Worker:                                           │
│   ├─ Get live matches from MongoDB                      │
│   ├─ Crawl FlashScore/LiveScore                         │
│   ├─ Parse score, minute, events                        │
│   └─ Detect changes                                     │
└────────────────┬─────────────────────────────────────────┘
                 │
                 │ If changes detected
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 2. DATABASE UPDATE                                       │
├──────────────────────────────────────────────────────────┤
│ MatchService:                                            │
│   ├─ Validate data                                       │
│   ├─ Update MongoDB (matches collection)                │
│   └─ Return success                                      │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 3. CACHE INVALIDATION                                    │
├──────────────────────────────────────────────────────────┤
│ CacheService:                                            │
│   ├─ Delete: cache:match:{id}                           │
│   ├─ Delete: cache:matches:live                         │
│   └─ Delete: cache:matches:today                        │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 4. NOTIFICATION PUBLISHING                               │
├──────────────────────────────────────────────────────────┤
│ NotificationService:                                     │
│   ├─ Build message                                       │
│   ├─ Redis PUBLISH to "match:{id}"                      │
│   └─ Redis PUBLISH to "live:all"                        │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 5. REDIS PUB/SUB                                         │
├──────────────────────────────────────────────────────────┤
│ Redis Listener (Background Task):                       │
│   ├─ Subscribed to "match:*", "live:*"                  │
│   ├─ Receives message                                    │
│   └─ Parse JSON                                          │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 6. WEBSOCKET BROADCASTING                                │
├──────────────────────────────────────────────────────────┤
│ ConnectionManager:                                       │
│   ├─ Get subscribers for "match:{id}"                   │
│   ├─ For each WebSocket connection:                     │
│   │   └─ ws.send_json(message)                          │
│   └─ Track failed connections                           │
└────────────────┬─────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────┐
│ 7. CLIENT UPDATE                                         │
├──────────────────────────────────────────────────────────┤
│ Browser (SvelteKit):                                     │
│   ├─ ws.onmessage receives data                         │
│   ├─ Update Svelte store                                │
│   │   matchesStore.updateMatch(id, data)                │
│   └─ Reactive UI updates automatically                   │
│       ├─ Score changes                                   │
│       ├─ Minute updates                                  │
│       └─ Event notifications                             │
└──────────────────────────────────────────────────────────┘
```

---

## 7. FRONTEND DESIGN

### 7.1 SvelteKit Pages Breakdown

#### 7.1.1 Home Page (Live Scores)

```svelte
<!-- src/routes/+page.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { matchesStore } from '$stores/matches';
  import { websocketStore } from '$stores/websocket';
  import MatchCard from '$components/MatchCard.svelte';
  import LoadingSpinner from '$components/LoadingSpinner.svelte';
  import LiveIndicator from '$components/LiveIndicator.svelte';

  let liveMatches = [];
  let todayMatches = [];
  let loading = true;

  onMount(async () => {
    // Fetch initial data
    await Promise.all([
      matchesStore.fetchLiveMatches(),
      matchesStore.fetchTodayMatches()
    ]);

    loading = false;

    // Subscribe to live updates
    websocketStore.subscribe('live:all');

    // Listen to store changes
    matchesStore.subscribe(state => {
      liveMatches = state.live;
      todayMatches = state.today;
    });
  });
</script>

<svelte:head>
  <title>Live Football Scores - Football Live</title>
  <meta name="description" content="Real-time football live scores and match updates" />
</svelte:head>

<div class="space-y-8">
  <!-- Live Matches Section -->
  <section>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-2xl font-bold flex items-center gap-2">
        <LiveIndicator />
        Live Matches
      </h2>
      <span class="text-sm text-gray-500">
        {liveMatches.length} matches
      </span>
    </div>

    {#if loading}
      <LoadingSpinner />
    {:else if liveMatches.length === 0}
      <div class="card text-center py-12 text-gray-500">
        <p class="text-lg">No live matches at the moment</p>
        <p class="text-sm mt-2">Check back soon for live updates!</p>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each liveMatches as match (match._id)}
          <MatchCard {match} />
        {/each}
      </div>
    {/if}
  </section>

  <!-- Today's Matches Section -->
  <section>
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-2xl font-bold">Today's Matches</h2>
      <span class="text-sm text-gray-500">
        {todayMatches.length} matches
      </span>
    </div>

    {#if loading}
      <LoadingSpinner />
    {:else if todayMatches.length === 0}
      <div class="card text-center py-12 text-gray-500">
        <p class="text-lg">No matches scheduled for today</p>
      </div>
    {:else}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {#each todayMatches as match (match._id)}
          <MatchCard {match} />
        {/each}
      </div>
    {/if}
  </section>
</div>
```

**Component Breakdown:**
- `MatchCard`: Display single match with score, teams, time
- `LiveIndicator`: Pulsing red dot for live matches
- `LoadingSpinner`: Loading state

**State Management:**
- `matchesStore`: Svelte store for match data
- `websocketStore`: WebSocket connection management

**Real-time Updates:**
- Subscribe to `live:all` channel on mount
- Listen to store updates
- Reactive UI updates automatically

---

Let me continue with the rest of the detailed plan. Due to the length, I'll create the file now:


## 8. IMPLEMENTATION ROADMAP

### 8.1 Phase 1: MVP Foundation (Weeks 1-4)

#### Week 1: Backend Setup

**Day 1-2: Project Structure**
- [ ] Create project directory structure
- [ ] Initialize Git repository
- [ ] Setup virtual environment
- [ ] Create requirements.txt
- [ ] Setup .env.example
- [ ] Create README.md

**Day 3-4: Database Setup**
- [ ] Install PostgreSQL, MongoDB, Redis (Docker)
- [ ] Create database schemas (PostgreSQL)
- [ ] Setup SQLAlchemy models
- [ ] Create MongoDB collections with indexes
- [ ] Configure Redis connection
- [ ] Test all database connections

**Day 5-7: FastAPI Core**
- [ ] Create FastAPI app structure
- [ ] Implement config management (Pydantic Settings)
- [ ] Setup database connections (async)
- [ ] Create health check endpoint
- [ ] Implement logging (structlog)
- [ ] Setup CORS middleware

#### Week 2: Authentication & Core APIs

**Day 8-9: Authentication**
- [ ] Implement JWT token generation/validation
- [ ] Create User model (PostgreSQL)
- [ ] Password hashing (bcrypt)
- [ ] POST /auth/register endpoint
- [ ] POST /auth/login endpoint
- [ ] GET /auth/me endpoint
- [ ] Test authentication flow

**Day 10-12: Core API Endpoints**
- [ ] Create Pydantic schemas (Match, League, Team)
- [ ] Implement MatchService with MongoDB
- [ ] GET /matches/live endpoint
- [ ] GET /matches/today endpoint
- [ ] GET /matches/{id} endpoint
- [ ] GET /leagues endpoint
- [ ] GET /leagues/{id}/table endpoint
- [ ] Test all endpoints with Postman

**Day 13-14: WebSocket Server**
- [ ] Implement ConnectionManager class
- [ ] Create WebSocket endpoint (/ws)
- [ ] Implement subscribe/unsubscribe logic
- [ ] Test WebSocket with wscat/Postman
- [ ] Document WebSocket protocol

#### Week 3: Crawling System

**Day 15-16: Base Crawler**
- [ ] Create BaseCrawler abstract class
- [ ] Implement user-agent rotation
- [ ] Implement proxy rotation (optional)
- [ ] Create retry logic with exponential backoff
- [ ] Add rate limiting per domain
- [ ] Test with sample URLs

**Day 17-19: FlashScore Crawler**
- [ ] Study FlashScore HTML structure
- [ ] Implement FlashScoreCrawler class
- [ ] Parse live score data
- [ ] Parse match events
- [ ] Parse match statistics
- [ ] Test with real match URLs
- [ ] Handle errors gracefully

**Day 20-21: Celery Setup**
- [ ] Install Celery + Redis
- [ ] Create celery_app.py configuration
- [ ] Create live_scores task
- [ ] Create fixtures task
- [ ] Create stats task
- [ ] Configure Celery Beat schedule
- [ ] Test tasks manually

#### Week 4: Integration & Testing

**Day 22-23: Crawl-to-DB Integration**
- [ ] Integrate crawler with MatchService
- [ ] Save crawled data to MongoDB
- [ ] Implement data validation
- [ ] Handle duplicate detection
- [ ] Test end-to-end crawl flow
- [ ] Monitor crawl job logs

**Day 24-25: Real-time Notifications**
- [ ] Create NotificationService
- [ ] Implement Redis Pub/Sub
- [ ] Publish match updates to Redis
- [ ] Create Redis listener background task
- [ ] Integrate with WebSocket broadcasting
- [ ] Test real-time updates end-to-end

**Day 26-28: MVP Testing & Bug Fixes**
- [ ] Write unit tests for services
- [ ] Write API endpoint tests
- [ ] Test WebSocket subscriptions
- [ ] Test crawling tasks
- [ ] Fix bugs and issues
- [ ] Document known issues

### 8.2 Phase 2: Frontend Development (Weeks 5-6)

#### Week 5: SvelteKit Setup & Core Pages

**Day 29-30: Project Setup**
- [ ] Create SvelteKit project
- [ ] Install TailwindCSS
- [ ] Configure TypeScript
- [ ] Setup environment variables
- [ ] Create app layout
- [ ] Design color scheme

**Day 31-32: Core Components**
- [ ] Create MatchCard component
- [ ] Create LiveIndicator component
- [ ] Create LoadingSpinner component
- [ ] Create ErrorMessage component
- [ ] Test components in Storybook (optional)

**Day 33-35: State Management**
- [ ] Create WebSocket store
- [ ] Create matches store
- [ ] Create auth store
- [ ] Implement API client (Axios)
- [ ] Test stores independently

#### Week 6: Pages & Real-time Integration

**Day 36-37: Home Page**
- [ ] Create home page layout
- [ ] Implement live matches section
- [ ] Implement today's matches section
- [ ] Add loading states
- [ ] Add error handling

**Day 38-39: Match Detail Page**
- [ ] Create match detail route
- [ ] Display match info, score, events
- [ ] Show match statistics
- [ ] Display lineups
- [ ] Add real-time updates

**Day 40-42: WebSocket Integration**
- [ ] Connect WebSocket on app mount
- [ ] Subscribe to live:all channel
- [ ] Handle incoming messages
- [ ] Update stores reactively
- [ ] Test real-time updates
- [ ] Handle connection errors

### 8.3 Phase 3: Enhancement (Weeks 7-8)

#### Week 7: Additional Features

**Day 43-44: League Pages**
- [ ] Create leagues list page
- [ ] Create league detail page
- [ ] Display league table
- [ ] Show league fixtures
- [ ] Add league filtering

**Day 45-46: Team Pages**
- [ ] Create team detail page
- [ ] Display team fixtures
- [ ] Show team statistics
- [ ] Add team squad (future)

**Day 47-49: User Features**
- [ ] Create login page
- [ ] Create register page
- [ ] Implement favorites functionality
- [ ] Create profile page
- [ ] Add favorite teams/leagues to home

#### Week 8: Polish & UX

**Day 50-51: UI Improvements**
- [ ] Add animations/transitions
- [ ] Improve mobile responsiveness
- [ ] Add skeleton loaders
- [ ] Implement dark mode (optional)
- [ ] Optimize images

**Day 52-54: Testing & Fixes**
- [ ] Cross-browser testing
- [ ] Mobile device testing
- [ ] Fix UI bugs
- [ ] Performance optimization
- [ ] Accessibility improvements

**Day 55-56: Documentation**
- [ ] Write API documentation
- [ ] Create deployment guide
- [ ] Document environment setup
- [ ] Create user guide (basic)

### 8.4 Phase 4: Production Readiness (Weeks 9-10)

#### Week 9: Docker & Deployment Prep

**Day 57-58: Docker Setup**
- [ ] Create Dockerfile for backend
- [ ] Create docker-compose.yml
- [ ] Test Docker build
- [ ] Configure volumes
- [ ] Setup network

**Day 59-60: Production Config**
- [ ] Setup production environment variables
- [ ] Configure production databases
- [ ] Setup SSL certificates
- [ ] Configure Nginx reverse proxy
- [ ] Setup domain/DNS

**Day 61-63: Deployment**
- [ ] Deploy to production server (AWS/Heroku/VPS)
- [ ] Configure database backups
- [ ] Setup monitoring (basic)
- [ ] Configure logging
- [ ] Test production deployment

#### Week 10: Monitoring & Launch

**Day 64-65: Monitoring Setup**
- [ ] Setup Prometheus metrics
- [ ] Configure Grafana dashboards
- [ ] Setup error tracking (Sentry)
- [ ] Configure alerts (email/Slack)
- [ ] Test monitoring

**Day 66-67: Load Testing**
- [ ] Write load test scripts
- [ ] Run load tests (100 concurrent users)
- [ ] Identify bottlenecks
- [ ] Optimize slow endpoints
- [ ] Re-test

**Day 68-70: Launch**
- [ ] Final QA testing
- [ ] Create backup plan
- [ ] Launch to production
- [ ] Monitor closely
- [ ] Fix critical bugs

### 8.5 Post-Launch (Weeks 11-12)

- [ ] Collect user feedback
- [ ] Fix bugs reported by users
- [ ] Optimize based on real usage
- [ ] Add more data sources
- [ ] Implement player statistics
- [ ] Plan next features

---

## 9. TESTING STRATEGY

### 9.1 Backend Testing

#### 9.1.1 Unit Tests

```python
# Test structure
tests/
├── test_api/
│   ├── test_auth.py
│   ├── test_matches.py
│   ├── test_leagues.py
│   └── test_teams.py
├── test_crawlers/
│   ├── test_base_crawler.py
│   ├── test_flashscore.py
│   └── test_parsers.py
├── test_services/
│   ├── test_match_service.py
│   ├── test_cache_service.py
│   └── test_notification_service.py
└── conftest.py  # Pytest fixtures
```

**Example Test:**

```python
# tests/test_api/test_matches.py

import pytest
from httpx import AsyncClient
from api.main import app


@pytest.mark.asyncio
async def test_get_live_matches():
    """Test GET /api/v1/matches/live"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/matches/live")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_match_by_id(test_match):
    """Test GET /api/v1/matches/{id}"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/api/v1/matches/{test_match['_id']}")

        assert response.status_code == 200
        data = response.json()
        assert data['_id'] == test_match['_id']
        assert 'score' in data
        assert 'home_team' in data


@pytest.mark.asyncio
async def test_get_match_not_found():
    """Test 404 for non-existent match"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/matches/nonexistent")

        assert response.status_code == 404
```

#### 9.1.2 Integration Tests

```python
# tests/integration/test_crawl_flow.py

@pytest.mark.asyncio
async def test_full_crawl_flow():
    """Test complete crawl-to-websocket flow"""

    # 1. Trigger crawl task
    result = crawl_live_scores.delay()
    result.wait(timeout=30)

    assert result.successful()

    # 2. Check database updated
    match = await db.matches.find_one({"external_id": "test_match_123"})
    assert match is not None
    assert match['score']['home'] > 0

    # 3. Check cache invalidated
    cached = await redis.get("cache:match:test_match_123")
    assert cached is None

    # 4. Check notification published
    # (Would need to setup Redis pub/sub listener)
```

#### 9.1.3 Test Coverage Goals

```
Target Coverage: 80%+

Critical Components (95%+):
- Authentication logic
- Match data validation
- Payment processing (future)

High Priority (85%+):
- API endpoints
- Service layer
- Crawling parsers

Medium Priority (70%+):
- Utility functions
- Background tasks
```

### 9.2 Frontend Testing

#### 9.2.1 Component Tests (Vitest + Testing Library)

```typescript
// tests/components/MatchCard.test.ts

import { render, screen } from '@testing-library/svelte';
import MatchCard from '$components/MatchCard.svelte';

describe('MatchCard', () => {
  const mockMatch = {
    _id: '123',
    home_team: { name: 'Manchester United', logo: 'url' },
    away_team: { name: 'Liverpool', logo: 'url' },
    score: { home: 2, away: 1 },
    status: 'live',
    minute: 67
  };

  it('renders match teams', () => {
    render(MatchCard, { props: { match: mockMatch } });

    expect(screen.getByText('Manchester United')).toBeInTheDocument();
    expect(screen.getByText('Liverpool')).toBeInTheDocument();
  });

  it('displays correct score', () => {
    render(MatchCard, { props: { match: mockMatch } });

    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('shows live indicator for live matches', () => {
    render(MatchCard, { props: { match: mockMatch } });

    expect(screen.getByText('67\'')).toBeInTheDocument();
  });
});
```

#### 9.2.2 E2E Tests (Playwright)

```typescript
// tests/e2e/live-scores.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Live Scores Page', () => {
  test('displays live matches', async ({ page }) => {
    await page.goto('/');

    // Wait for matches to load
    await page.waitForSelector('.match-card');

    // Check header
    await expect(page.locator('h2')).toContainText('Live Matches');

    // Check at least one match is displayed
    const matchCards = page.locator('.match-card');
    await expect(matchCards).toHaveCountGreaterThan(0);
  });

  test('updates score in real-time', async ({ page }) => {
    await page.goto('/');

    // Get initial score
    const scoreElement = page.locator('.match-card').first().locator('.score');
    const initialScore = await scoreElement.textContent();

    // Wait for WebSocket update (mock or use test fixture)
    await page.waitForTimeout(5000);

    // Check if score updated
    const newScore = await scoreElement.textContent();
    // In real scenario, you'd trigger a test WebSocket message
  });
});
```

### 9.3 Load Testing

#### 9.3.1 API Load Test (Locust)

```python
# locustfile.py

from locust import HttpUser, task, between

class FootballAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task(10)
    def get_live_matches(self):
        """Most common endpoint"""
        self.client.get("/api/v1/matches/live")

    @task(5)
    def get_today_matches(self):
        self.client.get("/api/v1/matches/today")

    @task(3)
    def get_leagues(self):
        self.client.get("/api/v1/leagues")

    @task(2)
    def get_match_detail(self):
        # Use a known match ID
        self.client.get("/api/v1/matches/123")

    @task(1)
    def get_league_table(self):
        self.client.get("/api/v1/leagues/premier-league/table")
```

**Run Load Test:**

```bash
# 100 users, spawn rate 10/sec, run for 5 minutes
locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=5m
```

#### 9.3.2 WebSocket Load Test

```python
# websocket_load_test.py

import asyncio
import websockets
import json

async def websocket_client(client_id):
    """Single WebSocket client"""
    uri = "ws://localhost:8000/ws"

    async with websockets.connect(uri) as websocket:
        # Subscribe to all live matches
        await websocket.send(json.dumps({
            'action': 'subscribe',
            'channels': ['live:all']
        }))

        # Keep connection open
        while True:
            message = await websocket.recv()
            print(f"Client {client_id}: {message}")

async def load_test(num_clients=1000):
    """Simulate multiple concurrent WebSocket connections"""
    tasks = [
        websocket_client(i)
        for i in range(num_clients)
    ]

    await asyncio.gather(*tasks)

# Run
asyncio.run(load_test(num_clients=1000))
```

### 9.4 Security Testing

- [ ] SQL Injection testing (automated with sqlmap)
- [ ] XSS testing (automated with XSStrike)
- [ ] CSRF protection validation
- [ ] Authentication bypass attempts
- [ ] Rate limiting effectiveness
- [ ] JWT token security
- [ ] API input validation
- [ ] Dependency vulnerability scan (safety, bandit)

---

## 10. DEPLOYMENT PLAN

### 10.1 Infrastructure Options

#### 10.1.1 Option A: AWS (Scalable)

```
Components:
├── ECS Fargate (FastAPI containers)
│   ├── Auto-scaling based on CPU
│   ├── 2-10 tasks
│   └── ALB (Application Load Balancer)
├── ECS Fargate (Celery workers)
│   ├── Separate task definition
│   └── Auto-scaling based on queue length
├── RDS PostgreSQL (Multi-AZ)
│   ├── db.t3.small (development)
│   ├── db.t3.medium (production)
│   └── Automated backups
├── DocumentDB / MongoDB Atlas
│   ├── 3-node replica set
│   └── Automated backups
├── ElastiCache Redis (Cluster mode)
│   ├── cache.t3.small
│   └── Multi-AZ
├── S3 + CloudFront
│   ├── Static assets (logos, images)
│   └── Frontend build (SvelteKit static)
├── Route 53 (DNS)
└── CloudWatch (Monitoring + Logs)

Estimated Monthly Cost:
- ECS Fargate: $50-150
- RDS PostgreSQL: $30-80
- MongoDB Atlas: $57 (M10)
- ElastiCache: $40-80
- Data Transfer: $20-50
Total: ~$200-400/month
```

#### 10.1.2 Option B: DigitalOcean (Cost-Effective)

```
Components:
├── App Platform (FastAPI)
│   ├── Basic Plan: $5/month
│   ├── Professional: $12/month
│   └── Auto-scaling
├── Droplet (Celery Workers)
│   ├── 2GB RAM: $12/month
│   ├── 4GB RAM: $24/month
│   └── Manual setup
├── Managed PostgreSQL
│   ├── 1GB: $15/month
│   ├── 2GB: $30/month
│   └── Daily backups
├── MongoDB Atlas (Free tier or $9/month)
├── Managed Redis
│   ├── 1GB: $15/month
│   └── Automatic failover
├── Spaces (CDN)
│   └── $5/month
└── Monitoring (built-in)

Total: ~$60-120/month
```

#### 10.1.3 Option C: VPS (Maximum Control)

```
Single VPS:
├── Hetzner CPX31 (8GB RAM, 4 vCPU): €11.90/month
├── OR Contabo VPS M (16GB RAM): €8.99/month

Services on VPS:
├── Docker Compose
│   ├── FastAPI (2 containers)
│   ├── Celery Workers (2 containers)
│   ├── Celery Beat (1 container)
│   ├── PostgreSQL (1 container)
│   ├── MongoDB (1 container)
│   ├── Redis (1 container)
│   └── Nginx (1 container)
├── Supervisor (process management)
└── Automated backups to Backblaze B2

Total: ~€12-20/month (~$13-22)
```

### 10.2 Deployment Steps (VPS)

#### Step 1: Server Setup

```bash
# Connect to VPS
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Install Nginx
apt install nginx -y

# Install certbot for SSL
apt install certbot python3-certbot-nginx -y

# Create app user
adduser appuser
usermod -aG docker appuser
```

#### Step 2: Clone & Configure

```bash
# Clone repository
su - appuser
git clone https://github.com/yourusername/football-live-score.git
cd football-live-score

# Create production .env
cp backend/.env.example backend/.env
nano backend/.env

# Set production values:
# DEBUG=False
# SECRET_KEY=<generate-strong-key>
# DATABASE_URL=postgresql://...
# MONGO_URI=mongodb://...
# etc.
```

#### Step 3: Build & Start

```bash
# Build images
cd backend
docker-compose build

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Step 4: Nginx Configuration

```nginx
# /etc/nginx/sites-available/football-live

server {
    server_name yourdomain.com www.yourdomain.com;

    # Frontend (SvelteKit)
    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=60r/m;
    location /api {
        limit_req zone=api burst=20;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/football-live /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Reload Nginx
systemctl reload nginx

# Setup SSL
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### Step 5: Database Migrations

```bash
# Run Alembic migrations
docker-compose exec backend alembic upgrade head

# Create initial data (leagues, teams)
docker-compose exec backend python scripts/seed_data.py
```

#### Step 6: Setup Backups

```bash
# Create backup script
cat > /home/appuser/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U admin football_db > /backups/postgres_$DATE.sql

# Backup MongoDB
docker-compose exec -T mongodb mongodump --out=/backups/mongo_$DATE

# Compress
tar -czf /backups/backup_$DATE.tar.gz /backups/*_$DATE*

# Upload to Backblaze B2 (optional)
# b2 upload-file bucket-name /backups/backup_$DATE.tar.gz backup_$DATE.tar.gz

# Keep only last 7 days
find /backups -type f -mtime +7 -delete
EOF

chmod +x /home/appuser/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /home/appuser/backup.sh") | crontab -
```

### 10.3 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml

name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to VPS
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /home/appuser/football-live-score
            git pull origin main
            cd backend
            docker-compose build
            docker-compose up -d
            docker-compose exec backend alembic upgrade head
```

---

## 11. PERFORMANCE OPTIMIZATION

### 11.1 Database Optimization

```python
# MongoDB Query Optimization

# BAD - Fetches all fields
matches = await db.matches.find({"status": "live"}).to_list(100)

# GOOD - Projection (only needed fields)
matches = await db.matches.find(
    {"status": "live"},
    {
        "_id": 1,
        "home_team.name": 1,
        "away_team.name": 1,
        "score": 1,
        "minute": 1
    }
).to_list(100)

# Use indexes effectively
db.matches.create_index([("status", 1), ("match_date", -1)])

# Use aggregation pipeline for complex queries
pipeline = [
    {"$match": {"status": "live"}},
    {"$project": {
        "home_team": 1,
        "away_team": 1,
        "score": 1
    }},
    {"$limit": 50}
]
matches = await db.matches.aggregate(pipeline).to_list(50)
```

### 11.2 Caching Strategy

```python
# Multi-layer caching

# Layer 1: Redis cache (30s for live matches)
@cache_result("match_details", ttl=30)
async def get_live_match(match_id: str):
    return await db.matches.find_one({"_id": match_id})

# Layer 2: In-memory cache (5s)
from functools import lru_cache
from datetime import datetime, timedelta

class CacheWithTTL:
    def __init__(self, ttl_seconds=5):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                return value
        return None

    def set(self, key, value):
        self.cache[key] = (value, datetime.now())

memory_cache = CacheWithTTL(ttl_seconds=5)

# Layer 3: CDN for static assets
# Use CloudFront/CloudFlare for team logos, league logos
```

### 11.3 API Response Optimization

```python
# Pagination
@app.get("/api/v1/matches")
async def get_matches(
    skip: int = 0,
    limit: int = 50,  # Max 100
):
    matches = await db.matches.find().skip(skip).limit(limit).to_list(limit)
    return matches

# Compression (gzip)
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Response model optimization (exclude None values)
from pydantic import BaseModel

class MatchResponse(BaseModel):
    id: str
    score: dict

    class Config:
        # Exclude None values from JSON response
        json_encoders = {type(None): lambda v: None}
        exclude_none = True
```

### 11.4 Frontend Optimization

```typescript
// Code splitting
const MatchDetail = () => import('$lib/components/MatchDetail.svelte');

// Lazy loading images
<img
  src={team.logo}
  loading="lazy"
  alt={team.name}
/>

// Debounce search
import { debounce } from '$lib/utils';

const handleSearch = debounce((query) => {
  // Search API call
}, 300);

// Virtual scrolling for long lists (using svelte-virtual)
import { VirtualList } from 'svelte-virtual';

<VirtualList items={matches} let:item>
  <MatchCard match={item} />
</VirtualList>
```

---

## 12. SECURITY IMPLEMENTATION

### 12.1 Authentication Security

```python
# Strong password requirements
from pydantic import validator
import re

class UserCreate(BaseModel):
    password: str

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain digit')
        return v

# Rate limiting on auth endpoints
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/auth/login")
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login():
    pass

# JWT token expiration
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### 12.2 Input Validation

```python
# Pydantic models for all inputs
class MatchQuery(BaseModel):
    league_id: Optional[UUID]
    date: Optional[date]
    status: Optional[str]
    limit: int = Field(50, le=100)  # Max 100
    offset: int = Field(0, ge=0)

    @validator('status')
    def validate_status(cls, v):
        allowed = ['scheduled', 'live', 'finished']
        if v and v not in allowed:
            raise ValueError(f'Status must be one of {allowed}')
        return v

# SQL injection prevention (already handled by SQLAlchemy)
# MongoDB injection prevention
from bson.objectid import ObjectId

def safe_object_id(id_string: str):
    """Safely convert string to ObjectId"""
    try:
        return ObjectId(id_string)
    except:
        raise ValueError("Invalid ObjectId format")
```

### 12.3 API Security Headers

```python
# Security headers middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# HTTPS redirect (production only)
if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "*.yourdomain.com"]
)

# Custom security headers
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### 12.4 Environment Variables Security

```python
# Never commit .env files
# Use secrets management in production

# AWS Secrets Manager (production)
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Local development: use .env
# Production: use AWS Secrets Manager / HashiCorp Vault
```

---

## 13. MONITORING & MAINTENANCE

### 13.1 Application Monitoring

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app

# Counters
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

crawl_jobs_total = Counter(
    'crawl_jobs_total',
    'Total crawl jobs',
    ['source', 'status']
)

# Histograms (latency)
api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['endpoint']
)

crawl_duration = Histogram(
    'crawl_duration_seconds',
    'Crawl job duration',
    ['source']
)

# Gauges (current state)
active_websocket_connections = Gauge(
    'active_websocket_connections',
    'Active WebSocket connections'
)

live_matches_count = Gauge(
    'live_matches_count',
    'Number of currently live matches'
)

# Mount metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

### 13.2 Logging Strategy

```python
# Structured logging with structlog
import structlog

logger = structlog.get_logger()

# Log levels by importance
# DEBUG: Detailed info (development only)
# INFO: General info (crawl started, user logged in)
# WARNING: Unexpected but handled (rate limit, parsing error)
# ERROR: Error that needs attention (DB connection failed)
# CRITICAL: System failure (all workers down)

# Example usage
logger.info(
    "match_crawled",
    match_id=match_id,
    source="flashscore",
    duration_ms=duration
)

logger.error(
    "crawl_failed",
    match_id=match_id,
    error=str(e),
    traceback=traceback.format_exc()
)

# Log to file + stdout
# Production: Use log aggregation (ELK stack, Datadog, Papertrail)
```

### 13.3 Alerts Configuration

```yaml
# Grafana alerts (alerts.yml)

groups:
  - name: api_alerts
    interval: 1m
    rules:
      - alert: HighErrorRate
        expr: rate(api_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High API error rate"
          description: "{{ $value }}% of requests are failing"

      - alert: HighLatency
        expr: histogram_quantile(0.95, api_request_duration_seconds) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency"

      - alert: NoLiveMatches
        expr: live_matches_count == 0
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "No live matches detected for 30 minutes"

  - name: crawler_alerts
    interval: 1m
    rules:
      - alert: CrawlFailureRate
        expr: rate(crawl_jobs_total{status="failed"}[10m]) > 0.2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High crawl failure rate"

      - alert: DatabaseDown
        expr: up{job="postgresql"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL database is down"
```

### 13.4 Maintenance Tasks

```bash
# Daily maintenance script

#!/bin/bash
# /home/appuser/maintenance.sh

# Clean up old matches (older than 30 days)
docker-compose exec mongodb mongo football_live --eval "
  db.matches.deleteMany({
    match_date: {\$lt: new Date(Date.now() - 30*24*60*60*1000)},
    status: 'finished'
  })
"

# Clean up old crawl jobs (older than 7 days)
docker-compose exec postgres psql -U admin -d football_db -c "
  DELETE FROM crawl_jobs
  WHERE created_at < NOW() - INTERVAL '7 days';
"

# Vacuum databases
docker-compose exec postgres psql -U admin -d football_db -c "VACUUM ANALYZE;"

# Clear Redis old keys
docker-compose exec redis redis-cli --scan --pattern "cache:*" | xargs docker-compose exec redis redis-cli del

# Check disk space
df -h

# Rotate logs
find /var/log/football-live -name "*.log" -mtime +7 -delete

# Backup
/home/appuser/backup.sh
```

```bash
# Add to crontab
0 3 * * * /home/appuser/maintenance.sh
```

---

## 14. CONCLUSION

This comprehensive plan provides a complete roadmap for implementing a production-ready football live score application with:

✅ **Detailed Architecture** - Microservices, databases, caching  
✅ **Complete API Design** - REST endpoints, WebSocket protocol  
✅ **Crawling Strategy** - Multi-source data collection  
✅ **Real-time Updates** - WebSocket + Redis Pub/Sub  
✅ **Frontend Implementation** - SvelteKit with real-time UI  
✅ **Testing Strategy** - Unit, integration, E2E, load tests  
✅ **Deployment Plan** - Multiple hosting options  
✅ **Performance Optimization** - Caching, indexing, lazy loading  
✅ **Security** - Authentication, validation, headers  
✅ **Monitoring** - Metrics, logging, alerts  

### Next Steps

1. **Start with MVP** (Weeks 1-4)
2. **Iterate based on feedback**
3. **Add features incrementally**
4. **Monitor and optimize**
5. **Scale as needed**

### Success Metrics

- **Uptime**: 99.5%+
- **API Latency**: < 200ms (p95)
- **Live Score Delay**: < 30s
- **User Satisfaction**: 4.5+ stars
- **Crawl Success Rate**: > 95%

---

**Good luck building your Football Live Score application! ⚽🚀**

