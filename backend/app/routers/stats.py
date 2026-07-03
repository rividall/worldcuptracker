from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Match, Scorer, Team
from app.routers._serializers import match_out, scorer_out, team_out
from app.schemas import (
    CupNumbersOut,
    StatMatchOut,
    StatTeamOut,
    SuperlativesOut,
    TournamentTotalsOut,
)

router = APIRouter(prefix="/api/v1/stats", tags=["stats"])

LEADERBOARD_LIMIT = 15


@router.get("", response_model=CupNumbersOut)
async def cup_numbers(db: AsyncSession = Depends(get_db)) -> CupNumbersOut:
    """Tournament-wide numbers for the Cup Numbers tab.

    Totals + team superlatives are computed across all matches; leaderboards come
    from the synced `scorers` table. Everything is derived from data we already
    hold — no external calls.
    """
    matches = (await db.execute(select(Match))).scalars().all()
    teams = {t.id: t for t in (await db.execute(select(Team))).scalars()}
    finished = [m for m in matches if m.status == "FINISHED" and m.home_score is not None]

    # --- Totals ---
    goals = sum((m.home_score or 0) + (m.away_score or 0) for m in finished)
    shootouts = sum(1 for m in matches if m.duration == "PENALTY_SHOOTOUT")
    extra_time = sum(1 for m in matches if m.duration == "EXTRA_TIME")
    clean_sheets = sum(
        (1 if m.away_score == 0 else 0) + (1 if m.home_score == 0 else 0) for m in finished
    )
    totals = TournamentTotalsOut(
        goals=goals,
        matches_played=len(finished),
        matches_total=len(matches),
        goals_per_match=round(goals / len(finished), 2) if finished else 0.0,
        shootouts=shootouts,
        extra_time=extra_time,
        clean_sheets=clean_sheets,
    )

    # --- Per-team aggregates across every match (group + knockout) ---
    gf: dict[int, int] = defaultdict(int)
    ga: dict[int, int] = defaultdict(int)
    clean: dict[int, int] = defaultdict(int)
    played: dict[int, int] = defaultdict(int)
    for m in finished:
        for team_id, scored, conceded in (
            (m.home_team_id, m.home_score, m.away_score),
            (m.away_team_id, m.away_score, m.home_score),
        ):
            if team_id is None:
                continue
            gf[team_id] += scored
            ga[team_id] += conceded
            played[team_id] += 1
            if conceded == 0:
                clean[team_id] += 1

    def _team_stat(team_id: int | None, value: int) -> StatTeamOut | None:
        team = teams.get(team_id) if team_id is not None else None
        if team is None:
            return None
        return StatTeamOut(team=team_out(team), value=value)

    best_attack = best_defense = most_clean = None
    if played:
        atk = max(played, key=lambda t: (gf[t], -ga[t]))
        best_attack = _team_stat(atk, gf[atk])
        # fewest conceded, tie-break toward more matches played (harder to keep low)
        dfn = min(played, key=lambda t: (ga[t], -played[t]))
        best_defense = _team_stat(dfn, ga[dfn])
        cln = max(played, key=lambda t: (clean[t], played[t]))
        most_clean = _team_stat(cln, clean[cln])

    # --- Match superlatives ---
    biggest_win = highest_scoring = None
    if finished:
        bw = max(finished, key=lambda m: (abs(m.home_score - m.away_score), m.home_score + m.away_score))
        biggest_win = StatMatchOut(
            match=match_out(bw, teams), value=abs(bw.home_score - bw.away_score)
        )
        hs = max(finished, key=lambda m: (m.home_score + m.away_score, abs(m.home_score - m.away_score)))
        highest_scoring = StatMatchOut(match=match_out(hs, teams), value=hs.home_score + hs.away_score)

    superlatives = SuperlativesOut(
        best_attack=best_attack,
        best_defense=best_defense,
        most_clean_sheets=most_clean,
        biggest_win=biggest_win,
        highest_scoring=highest_scoring,
    )

    # --- Leaderboards ---
    top_scorers = (
        (
            await db.execute(
                select(Scorer)
                .order_by(Scorer.goals.desc(), Scorer.assists.desc().nullslast())
                .limit(LEADERBOARD_LIMIT)
            )
        )
        .scalars()
        .all()
    )
    top_assisters = (
        (
            await db.execute(
                select(Scorer)
                .where(Scorer.assists.is_not(None), Scorer.assists > 0)
                .order_by(Scorer.assists.desc(), Scorer.goals.desc())
                .limit(LEADERBOARD_LIMIT)
            )
        )
        .scalars()
        .all()
    )

    return CupNumbersOut(
        totals=totals,
        top_scorers=[scorer_out(s, teams) for s in top_scorers],
        top_assisters=[scorer_out(s, teams) for s in top_assisters],
        superlatives=superlatives,
    )
