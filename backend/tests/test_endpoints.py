"""Endpoint tests against the SQLite test DB with seeded data."""

from datetime import datetime, timezone

import pytest

from app.models import GroupStanding, Match, SyncRun, Team
from tests.conftest import test_session

KICKOFF = datetime(2026, 6, 11, 20, 0, tzinfo=timezone.utc)


async def _seed():
    async with test_session() as session:
        session.add_all(
            [
                Team(id=1, name="Mexico", tla="MEX", crest_url="http://x/mex.svg", group_name="A"),
                Team(id=2, name="Canada", tla="CAN", crest_url="http://x/can.svg", group_name="A"),
                Team(id=3, name="France", tla="FRA", crest_url="http://x/fra.svg"),
            ]
        )
        session.add_all(
            [
                GroupStanding(
                    group_name="A", team_id=1, position=1, played=3, won=3, drawn=0,
                    lost=0, goals_for=6, goals_against=2, goal_difference=4, points=9,
                ),
                GroupStanding(
                    group_name="A", team_id=2, position=2, played=3, won=1, drawn=1,
                    lost=1, goals_for=3, goals_against=3, goal_difference=0, points=4,
                ),
            ]
        )
        session.add_all(
            [
                Match(
                    id=100, stage="GROUP_STAGE", group_name="A", utc_date=KICKOFF,
                    status="FINISHED", home_team_id=1, away_team_id=2,
                    home_score=2, away_score=0, winner_team_id=1,
                ),
                Match(
                    id=200, stage="FINAL", utc_date=KICKOFF, status="TIMED",
                    home_team_id=None, away_team_id=None,
                ),
                Match(
                    id=201, stage="SEMI_FINALS", utc_date=KICKOFF, status="FINISHED",
                    home_team_id=3, away_team_id=1, home_score=1, away_score=0,
                    winner_team_id=3,
                ),
            ]
        )
        session.add(
            SyncRun(
                started_at=KICKOFF, finished_at=KICKOFF, status="success",
                matches_updated=3, detail="3 matches touched",
            )
        )
        await session.commit()


@pytest.mark.asyncio
async def test_groups(client):
    await _seed()
    response = await client.get("/api/v1/groups")
    assert response.status_code == 200
    groups = response.json()
    assert len(groups) == 1
    group = groups[0]
    assert group["name"] == "A"
    assert group["standings"][0]["team"]["tla"] == "MEX"
    assert group["standings"][0]["points"] == 9
    assert group["matches"][0]["score"] == {
        "home": 2, "away": 0, "penalties_home": None, "penalties_away": None,
        "duration": "REGULAR",
    }


@pytest.mark.asyncio
async def test_matches_filter(client):
    await _seed()
    response = await client.get("/api/v1/matches?stage=GROUP_STAGE")
    assert response.status_code == 200
    assert [m["id"] for m in response.json()] == [100]


@pytest.mark.asyncio
async def test_bracket(client):
    await _seed()
    response = await client.get("/api/v1/bracket")
    assert response.status_code == 200
    bracket = response.json()
    stages = [r["stage"] for r in bracket["rounds"]]
    assert stages == ["LAST_32", "LAST_16", "QUARTER_FINALS", "SEMI_FINALS", "FINAL"]
    final_round = bracket["rounds"][-1]
    assert final_round["matches"][0]["position"] == 0
    semi = bracket["rounds"][-2]["matches"][0]
    assert semi["feeds_into_match_id"] == 200
    assert bracket["champion_team_id"] is None


@pytest.mark.asyncio
async def test_last_sync(client):
    await _seed()
    response = await client.get("/api/v1/meta/last-sync")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["matches_updated"] == 3


@pytest.mark.asyncio
async def test_last_sync_empty(client):
    response = await client.get("/api/v1/meta/last-sync")
    assert response.status_code == 200
    assert response.json()["last_sync_at"] is None
