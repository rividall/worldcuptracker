from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import GroupStanding, Match, Scorer, Team
from app.routers._serializers import match_out, scorer_out, team_out
from app.schemas import StandingOut, TeamDetailOut, TeamListItemOut

router = APIRouter(prefix="/api/v1/teams", tags=["teams"])


@router.get("", response_model=list[TeamListItemOut])
async def list_teams(db: AsyncSession = Depends(get_db)) -> list[TeamListItemOut]:
    """All teams, for the My Team picker (grouped client-side by group)."""
    teams = (await db.execute(select(Team).order_by(Team.group_name, Team.name))).scalars().all()
    return [
        TeamListItemOut(
            id=t.id, name=t.name, tla=t.tla, crest_url=t.crest_url, group_name=t.group_name
        )
        for t in teams
    ]


@router.get("/{team_id}", response_model=TeamDetailOut)
async def team_detail(team_id: int, db: AsyncSession = Depends(get_db)) -> TeamDetailOut:
    """Everything the My Team page needs: standing, all matches, scorers.

    Presentation (form, summary stats, status badge) is derived on the frontend
    from these matches — the backend just serves the raw pieces.
    """
    team = await db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")

    teams = {t.id: t for t in (await db.execute(select(Team))).scalars()}

    matches = (
        (
            await db.execute(
                select(Match)
                .where(or_(Match.home_team_id == team_id, Match.away_team_id == team_id))
                .order_by(Match.utc_date, Match.id)
            )
        )
        .scalars()
        .all()
    )

    standing_row = (
        (await db.execute(select(GroupStanding).where(GroupStanding.team_id == team_id)))
        .scalars()
        .first()
    )
    standing = None
    if standing_row is not None:
        standing = StandingOut(
            position=standing_row.position,
            team=team_out(team),
            played=standing_row.played,
            won=standing_row.won,
            drawn=standing_row.drawn,
            lost=standing_row.lost,
            goals_for=standing_row.goals_for,
            goals_against=standing_row.goals_against,
            goal_difference=standing_row.goal_difference,
            points=standing_row.points,
        )

    scorer_rows = (
        (
            await db.execute(
                select(Scorer)
                .where(Scorer.team_id == team_id)
                .order_by(Scorer.goals.desc(), Scorer.assists.desc().nullslast())
            )
        )
        .scalars()
        .all()
    )
    return TeamDetailOut(
        team=team_out(team),
        group_name=team.group_name,
        standing=standing,
        matches=[match_out(m, teams) for m in matches],
        scorers=[scorer_out(s, teams) for s in scorer_rows],
    )
