"""Hourly sync: pull standings + matches from football-data.org, upsert into DB.

Rules (CLAUDE.md): only this service talks to the external API, never request
handlers. 2 requests per run, well under the 10 req/min free-tier limit.
"""

import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models import GroupStanding, Match, SyncRun, Team
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
        full_time = score.get("fullTime", {})
        penalties = score.get("penalties") or {}

        match.stage = data["stage"]
        match.group_name = normalize_group(data.get("group"))
        match.utc_date = _parse_dt(data["utcDate"])
        match.status = data["status"]
        match.home_team_id = data.get("homeTeam", {}).get("id")
        match.away_team_id = data.get("awayTeam", {}).get("id")
        match.home_score = full_time.get("home")
        match.away_score = full_time.get("away")
        match.duration = score.get("duration") or "REGULAR"
        match.penalties_home = penalties.get("home")
        match.penalties_away = penalties.get("away")
        match.winner_team_id = _winner_team_id(data)
        match.last_updated = new_last_updated
    return updated


async def _fetch_with_retry(client: FootballDataClient):
    last_error: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            standings = await client.get_standings()
            matches = await client.get_matches()
            return standings, matches
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
        standings_payload, matches_payload = await _fetch_with_retry(client)
        async with async_session() as session:
            await _sync_standings(session, standings_payload)
            updated = await _sync_matches(session, matches_payload)
            run = await session.get(SyncRun, run_id)
            run.finished_at = datetime.now(timezone.utc)
            run.status = "success"
            run.matches_updated = updated
            run.detail = f"{updated} matches touched"
            await session.commit()
        logger.info("Sync complete: %s matches touched", updated)
    except Exception as error:  # noqa: BLE001 — record failure, don't crash the loop
        logger.exception("Sync failed")
        async with async_session() as session:
            run = await session.get(SyncRun, run_id)
            run.finished_at = datetime.now(timezone.utc)
            run.status = "error"
            run.detail = str(error)[:2000]
            await session.commit()


async def sync_loop() -> None:
    """Background loop: sync now, then every FETCH_INTERVAL_MINUTES."""
    from app.core.config import settings

    while True:
        await run_sync()
        await asyncio.sleep(settings.FETCH_INTERVAL_MINUTES * 60)
