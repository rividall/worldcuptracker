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


class ScorerOut(BaseModel):
    player_id: int
    player_name: str
    nationality: str | None = None
    team_id: int | None = None
    team_tla: str | None = None
    team_crest: str | None = None
    goals: int
    assists: int | None = None
    penalties: int | None = None
    played_matches: int | None = None


class TeamListItemOut(TeamOut):
    group_name: str | None = None


class TeamDetailOut(BaseModel):
    team: TeamOut
    group_name: str | None = None
    standing: StandingOut | None = None
    matches: list[MatchOut]
    scorers: list[ScorerOut]


class TournamentTotalsOut(BaseModel):
    goals: int
    matches_played: int
    matches_total: int
    goals_per_match: float
    shootouts: int
    extra_time: int
    clean_sheets: int


class StatTeamOut(BaseModel):
    team: TeamOut
    value: int


class StatMatchOut(BaseModel):
    match: MatchOut
    value: int  # goal margin (biggest win) or combined goals (highest scoring)


class SuperlativesOut(BaseModel):
    best_attack: StatTeamOut | None = None
    best_defense: StatTeamOut | None = None
    most_clean_sheets: StatTeamOut | None = None
    biggest_win: StatMatchOut | None = None
    highest_scoring: StatMatchOut | None = None


class CupNumbersOut(BaseModel):
    totals: TournamentTotalsOut
    top_scorers: list[ScorerOut]
    top_assisters: list[ScorerOut]
    superlatives: SuperlativesOut
