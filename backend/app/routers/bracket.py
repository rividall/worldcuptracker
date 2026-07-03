from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Match, Team
from app.routers._serializers import match_out
from app.schemas import BracketMatchOut, BracketOut, RoundOut
from app.services.bracket import ROUND_ORDER, build_positions

router = APIRouter(prefix="/api/v1/bracket", tags=["bracket"])


@router.get("", response_model=BracketOut)
async def get_bracket(db: AsyncSession = Depends(get_db)) -> BracketOut:
    knockout = (
        (await db.execute(select(Match).where(Match.stage != "GROUP_STAGE"))).scalars().all()
    )
    teams = {t.id: t for t in (await db.execute(select(Team))).scalars()}

    tree = [m for m in knockout if m.stage in ROUND_ORDER]
    positions, feeds_into = build_positions(tree)

    rounds = []
    for stage in ROUND_ORDER:
        stage_matches = sorted(
            (m for m in tree if m.stage == stage), key=lambda m: positions[m.id]
        )
        rounds.append(
            RoundOut(
                stage=stage,
                matches=[
                    BracketMatchOut(
                        **match_out(m, teams).model_dump(),
                        position=positions[m.id],
                        feeds_into_match_id=feeds_into[m.id],
                    )
                    for m in stage_matches
                ],
            )
        )

    third = next((m for m in knockout if m.stage == "THIRD_PLACE"), None)
    final = next((m for m in tree if m.stage == "FINAL"), None)
    return BracketOut(
        rounds=rounds,
        third_place=match_out(third, teams) if third else None,
        champion_team_id=final.winner_team_id if final else None,
    )
