"""Hourly sync: pull standings + matches from football-data.org, upsert into DB.

Rules (CLAUDE.md): only this service talks to the external API, never request
handlers. 2 requests per run, well under the 10 req/min free-tier limit.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models import GroupStanding, Match, Scorer, SyncRun, Team
from app.services.football_data import FootballDataClient, normalize_group

logger = logging.getLogger(__name__)

RETRIES = 3
RETRY_DELAY_SECONDS = 10


def _parse_dt(raw: str | None) -> datetime | None:
    if not raw:
        return None
    return datetime.fromisoformat(raw.replace("Z", "+00:00"))


async def _upsert_team(session: AsyncSession, data: dict, group: str | None = None) -> None:
    if not data or data.get("id") is None:
        return
    team = await session.get(Team, data["id"])
    if team is None:
        team = Team(id=data["id"])
        session.add(team)
    team.name = data.get("name") or team.name or "TBD"
    team.tla = data.get("tla") or team.tla
    team.crest_url = data.get("crest") or team.crest_url
    if group:
        team.group_name = group
    # Persist the team now so the parent `teams` row exists before any
    # group_standings/matches row references it. SQLAlchemy orders flush-time
    # INSERTs by relationship() links, not bare ForeignKey columns — and we
    # declare none — so without this an autoflush can emit the child row first
    # and hit a ForeignKeyViolationError.
    await session.flush()


async def _sync_standings(session: AsyncSession, payload: dict) -> None:
    await session.execute(delete(GroupStanding))
    for block in payload.get("standings", []):
        group = normalize_group(block.get("group"))
        if not group or block.get("type") != "TOTAL":
            continue
        for row in block.get("table", []):
            await _upsert_team(session, row.get("team", {}), group=group)
            session.add(
                GroupStanding(
                    group_name=group,
                    team_id=row["team"]["id"],
                    position=row["position"],
                    played=row.get("playedGames", 0),
                    won=row.get("won", 0),
                    drawn=row.get("draw", 0),
                    lost=row.get("lost", 0),
                    goals_for=row.get("goalsFor", 0),
                    goals_against=row.get("goalsAgainst", 0),
                    goal_difference=row.get("goalDifference", 0),
                    points=row.get("points", 0),
                )
            )


def _winner_team_id(match_data: dict) -> int | None:
    winner = match_data.get("score", {}).get("winner")
    if winner == "HOME_TEAM":
        return match_data.get("homeTeam", {}).get("id")
    if winner == "AWAY_TEAM":
        return match_data.get("awayTeam", {}).get("id")
    return None


async def _sync_matches(session: AsyncSession, payload: dict) -> int:
    updated = 0
    for data in payload.get("matches", []):
        await _upsert_team(session, data.get("homeTeam", {}))
        await _upsert_team(session, data.get("awayTeam", {}))

        match = await session.get(Match, data["id"])
        if match is None:
            match = Match(id=data["id"], utc_date=_parse_dt(data["utcDate"]))
            session.add(match)

        new_last_updated = _parse_dt(data.get("lastUpdated"))
        if match.last_updated != new_last_updated:
            updated += 1

        score = data.get("score", {})
        full_time = score.get("fullTime") or {}
        regular_time = score.get("regularTime") or {}
        extra_time = score.get("extraTime") or {}
        penalties = score.get("penalties") or {}

        match.stage = data["stage"]
        match.group_name = normalize_group(data.get("group"))
        match.utc_date = _parse_dt(data["utcDate"])
        match.status = data["status"]
        match.home_team_id = data.get("homeTeam", {}).get("id")
        match.away_team_id = data.get("awayTeam", {}).get("id")
        # Store goals in play only (regular + extra time), never the shootout.
        # Prefer the regularTime/extraTime breakdown: football-data's fullTime is
        # unreliable for shootout matches — it sometimes doesn't reconcile with
        # reg+extra+pens (e.g. match 537428 reports fullTime 3-5 for a game that
        # was reg 1-1, pens 4-4, which naive subtraction would turn negative).
        # Plain matches carry no breakdown, so fall back to fullTime there. The
        # shootout stays in penalties_home/away.
        if regular_time.get("home") is not None:
            match.home_score = (regular_time.get("home") or 0) + (extra_time.get("home") or 0)
            match.away_score = (regular_time.get("away") or 0) + (extra_time.get("away") or 0)
        else:
            match.home_score = full_time.get("home")
            match.away_score = full_time.get("away")
        match.duration = score.get("duration") or "REGULAR"
        match.penalties_home = penalties.get("home")
        match.penalties_away = penalties.get("away")
        match.winner_team_id = _winner_team_id(data)
        match.last_updated = new_last_updated
    return updated


async def _sync_scorers(session: AsyncSession, payload: dict) -> int:
    """Replace the scorers table with the latest tournament top-scorer rows."""
    await session.execute(delete(Scorer))
    count = 0
    for row in payload.get("scorers", []):
        player = row.get("player") or {}
        team = row.get("team") or {}
        if player.get("id") is None or team.get("id") is None:
            continue
        # Ensure the team row exists (flushes) before the FK-bearing Scorer row.
        await _upsert_team(session, team)
        session.add(
            Scorer(
                player_id=player["id"],
                player_name=player.get("name") or "Unknown",
                nationality=player.get("nationality"),
                team_id=team["id"],
                goals=row.get("goals") or 0,
                assists=row.get("assists"),
                penalties=row.get("penalties"),
                played_matches=row.get("playedMatches"),
            )
        )
        count += 1
    return count


async def _fetch_with_retry(client: FootballDataClient):
    last_error: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            standings = await client.get_standings()
            matches = await client.get_matches()
            scorers = await client.get_scorers()
            return standings, matches, scorers
        except Exception as error:  # noqa: BLE001 — log and retry
            last_error = error
            logger.warning("Sync fetch attempt %s/%s failed: %s", attempt, RETRIES, error)
            if attempt < RETRIES:
                await asyncio.sleep(RETRY_DELAY_SECONDS * attempt)
    raise last_error  # type: ignore[misc]


async def run_sync() -> None:
    """One full sync run, recorded in sync_runs."""
    async with async_session() as session:
        run = SyncRun(started_at=datetime.now(timezone.utc), status="running")
        session.add(run)
        await session.commit()
        run_id = run.id

    client = FootballDataClient()
    try:
        standings_payload, matches_payload, scorers_payload = await _fetch_with_retry(client)
        async with async_session() as session:
            await _sync_standings(session, standings_payload)
            updated = await _sync_matches(session, matches_payload)
            scorers = await _sync_scorers(session, scorers_payload)
            run = await session.get(SyncRun, run_id)
            run.finished_at = datetime.now(timezone.utc)
            run.status = "success"
            run.matches_updated = updated
            run.detail = f"{updated} matches touched, {scorers} scorers"
            await session.commit()
        logger.info("Sync complete: %s matches touched, %s scorers", updated, scorers)
    except Exception as error:  # noqa: BLE001 — record failure, don't crash the loop
        logger.exception("Sync failed")
        async with async_session() as session:
            run = await session.get(SyncRun, run_id)
            run.finished_at = datetime.now(timezone.utc)
            run.status = "error"
            run.detail = str(error)[:2000]
            await session.commit()


LIVE_STATUSES = ("IN_PLAY", "PAUSED")
LIVE_WINDOW_BEFORE = timedelta(minutes=15)  # imminent kickoff
LIVE_WINDOW_AFTER = timedelta(hours=3)  # kicked off but not yet finished (covers ET/pens)


async def _has_live_window(session: AsyncSession) -> bool:
    """True if any match is in play or inside its kickoff window (not finished).

    Robust to the feed being slow to flip a match to IN_PLAY: a match whose
    kickoff is recent and isn't FINISHED counts as live.
    """
    now = datetime.now(timezone.utc)
    stmt = (
        select(func.count())
        .select_from(Match)
        .where(
            Match.status != "FINISHED",
            or_(
                Match.status.in_(LIVE_STATUSES),
                and_(
                    Match.utc_date >= now - LIVE_WINDOW_AFTER,
                    Match.utc_date <= now + LIVE_WINDOW_BEFORE,
                ),
            ),
        )
    )
    return bool((await session.execute(stmt)).scalar_one())


async def sync_loop() -> None:
    """Background loop: sync now, then wait — fast during live windows, hourly otherwise."""
    from app.core.config import settings

    while True:
        await run_sync()
        async with async_session() as session:
            live = await _has_live_window(session)
        minutes = (
            settings.LIVE_FETCH_INTERVAL_MINUTES if live else settings.FETCH_INTERVAL_MINUTES
        )
        logger.info("Next sync in %s min (live window: %s)", minutes, live)
        await asyncio.sleep(minutes * 60)
