"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import get_settings
from .database import init_db
from .routers import health, resumes, match

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    # Ensure storage directory exists
    storage_path = Path(settings.storage_root)
    storage_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Storage directory ready: {storage_path}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Resume Repository API",
    description="Production-grade resume versioning and job-matching system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(resumes.router, prefix=settings.api_prefix)
app.include_router(match.router, prefix=settings.api_prefix)

# Serve static frontend files (if built)
static_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
    logger.info(f"Serving static frontend from {static_dir}")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Resume Repository API",
        "version": "1.0.0",
        "docs": "/docs"
    }
