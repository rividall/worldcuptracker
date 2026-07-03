import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers.bracket import router as bracket_router
from app.routers.groups import router as groups_router
from app.routers.matches import router as matches_router
from app.routers.meta import router as meta_router
from app.routers.stats import router as stats_router
from app.routers.teams import router as teams_router

logger = logging.getLogger(__name__)


def _run_migrations() -> None:
    """Run Alembic migrations on startup (no-op if already at head)."""
    import subprocess

    try:
        subprocess.run(
            ["python", "-m", "alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
        )
    except Exception:
        pass  # Skip if alembic isn't available (e.g. during tests)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    _run_migrations()

    sync_task: asyncio.Task | None = None
    if settings.FOOTBALL_DATA_API_KEY and settings.FOOTBALL_DATA_API_KEY != "CHANGE_ME":
        from app.services.sync import sync_loop

        sync_task = asyncio.create_task(sync_loop())
        logger.info(
            "Started football-data.org sync loop (every %s min)",
            settings.FETCH_INTERVAL_MINUTES,
        )
    else:
        logger.warning("FOOTBALL_DATA_API_KEY not set — sync loop disabled")

    yield

    if sync_task:
        sync_task.cancel()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files (skipped when the dir can't be created, e.g. local tests)
_upload_path = Path(settings.UPLOAD_DIR)
try:
    _upload_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=_upload_path), name="uploads")
except OSError:
    logger.warning("Upload dir %s unavailable — /uploads not mounted", _upload_path)

app.include_router(groups_router)
app.include_router(matches_router)
app.include_router(bracket_router)
app.include_router(meta_router)
app.include_router(teams_router)
app.include_router(stats_router)


@app.get("/health")
async def health():
    return {"status": "healthy", "version": settings.APP_VERSION}
