from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import GroupStanding, Match, Team
from app.routers._serializers import match_out, team_out
from app.schemas import GroupOut, StandingOut

router = APIRouter(prefix="/api/v1/groups", tags=["groups"])


@router.get("", response_model=list[GroupOut])
async def list_groups(db: AsyncSession = Depends(get_db)) -> list[GroupOut]:
    teams = {t.id: t for t in (await db.execute(select(Team))).scalars()}
    standings = (
        (await db.execute(select(GroupStanding).order_by(GroupStanding.group_name, GroupStanding.position)))
        .scalars()
        .all()
    )
    group_matches = (
        (
            await db.execute(
                select(Match).where(Match.stage == "GROUP_STAGE").order_by(Match.utc_date, Match.id)
            )
        )
        .scalars()
        .all()
    )

    groups: dict[str, GroupOut] = {}
    for row in standings:
        group = groups.setdefault(row.group_name, GroupOut(name=row.group_name, standings=[], matches=[]))
        group.standings.append(
            StandingOut(
                position=row.position,
                team=team_out(teams[row.team_id]),
                played=row.played,
                won=row.won,
                drawn=row.drawn,
                lost=row.lost,
                goals_for=row.goals_for,
                goals_against=row.goals_against,
                goal_difference=row.goal_difference,
                points=row.points,
            )
        )
    for match in group_matches:
        if match.group_name in groups:
            groups[match.group_name].matches.append(match_out(match, teams))

    return [groups[name] for name in sorted(groups)]
