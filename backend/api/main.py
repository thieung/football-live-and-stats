"""
Football Live Score API - Main Application
FastAPI application with WebSocket support for real-time updates
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from datetime import datetime

from api.core.config import settings
from api.core.database import init_db, close_db
from api.routes import auth, matches, leagues, teams, users, websocket
from api.background import start_redis_listener, stop_redis_listener

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("application_startup", version=settings.API_VERSION)
    await init_db()

    # Start Redis listener for real-time updates
    import asyncio
    redis_listener_task = asyncio.create_task(start_redis_listener())
    logger.info("redis_listener_task_started")

    yield

    # Shutdown
    logger.info("application_shutdown")

    # Stop Redis listener
    await stop_redis_listener()

    # Cancel the listener task if still running
    if not redis_listener_task.done():
        redis_listener_task.cancel()
        try:
            await redis_listener_task
        except asyncio.CancelledError:
            pass

    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Real-time football live scores and statistics API",
    version=settings.API_VERSION,
    docs_url=f"/api/{settings.API_VERSION}/docs",
    redoc_url=f"/api/{settings.API_VERSION}/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.API_VERSION
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.API_VERSION,
        "docs": f"/api/{settings.API_VERSION}/docs",
        "health": "/health"
    }


# Include routers
app.include_router(
    auth.router,
    prefix=f"/api/{settings.API_VERSION}/auth",
    tags=["Authentication"]
)

app.include_router(
    matches.router,
    prefix=f"/api/{settings.API_VERSION}/matches",
    tags=["Matches"]
)

app.include_router(
    leagues.router,
    prefix=f"/api/{settings.API_VERSION}/leagues",
    tags=["Leagues"]
)

app.include_router(
    teams.router,
    prefix=f"/api/{settings.API_VERSION}/teams",
    tags=["Teams"]
)

app.include_router(
    users.router,
    prefix=f"/api/{settings.API_VERSION}/users",
    tags=["Users"]
)

# WebSocket endpoint
app.include_router(
    websocket.router,
    tags=["WebSocket"]
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
