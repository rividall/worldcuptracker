from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Match, Team
from app.routers._serializers import match_out
from app.schemas import MatchOut

router = APIRouter(prefix="/api/v1/matches", tags=["matches"])


@router.get("", response_model=list[MatchOut])
async def list_matches(
    stage: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> list[MatchOut]:
    query = select(Match).order_by(Match.utc_date, Match.id)
    if stage:
        query = query.where(Match.stage == stage.upper())
    if status:
        query = query.where(Match.status == status.upper())
    matches = (await db.execute(query)).scalars().all()
    teams = {t.id: t for t in (await db.execute(select(Team))).scalars()}
    return [match_out(m, teams) for m in matches]
