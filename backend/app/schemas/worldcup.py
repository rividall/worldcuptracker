from datetime import datetime

from pydantic import BaseModel


class TeamOut(BaseModel):
    id: int
    name: str
    tla: str | None = None
    crest_url: str | None = None


class ScoreOut(BaseModel):
    home: int | None = None
    away: int | None = None
    penalties_home: int | None = None
    penalties_away: int | None = None
    duration: str = "REGULAR"


class MatchOut(BaseModel):
    id: int
    stage: str
    group_name: str | None = None
    utc_date: datetime
    status: str
    home_team: TeamOut | None = None
    away_team: TeamOut | None = None
    score: ScoreOut
    winner_team_id: int | None = None


class StandingOut(BaseModel):
    position: int
    team: TeamOut
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


class GroupOut(BaseModel):
    name: str
    standings: list[StandingOut]
    matches: list[MatchOut]


class BracketMatchOut(MatchOut):
    position: int
    feeds_into_match_id: int | None = None


class RoundOut(BaseModel):
    stage: str
    matches: list[BracketMatchOut]


class BracketOut(BaseModel):
    rounds: list[RoundOut]
    third_place: MatchOut | None = None
    champion_team_id: int | None = None


class LastSyncOut(BaseModel):
    last_sync_at: datetime | None = None
    status: str | None = None
    matches_updated: int | None = None
    detail: str | None = None
