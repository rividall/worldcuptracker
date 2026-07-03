from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import SyncRun
from app.schemas import LastSyncOut

router = APIRouter(prefix="/api/v1/meta", tags=["meta"])


@router.get("/last-sync", response_model=LastSyncOut)
async def last_sync(db: AsyncSession = Depends(get_db)) -> LastSyncOut:
    run = (
        (
            await db.execute(
                select(SyncRun)
                .where(SyncRun.status != "running")
                .order_by(SyncRun.started_at.desc())
                .limit(1)
            )
        )
        .scalars()
        .first()
    )
    if run is None:
        return LastSyncOut()
    return LastSyncOut(
        last_sync_at=run.finished_at or run.started_at,
        status=run.status,
        matches_updated=run.matches_updated,
        detail=run.detail,
    )
