"""Shared ORM → schema serializers used by the routers."""

from app.models import Match, Team
from app.schemas import MatchOut, ScoreOut, TeamOut


def team_out(team: Team | None) -> TeamOut | None:
    if team is None:
        return None
    return TeamOut(id=team.id, name=team.name, tla=team.tla, crest_url=team.crest_url)


def match_out(match: Match, teams: dict[int, Team]) -> MatchOut:
    return MatchOut(
        id=match.id,
        stage=match.stage,
        group_name=match.group_name,
        utc_date=match.utc_date,
        status=match.status,
        home_team=team_out(teams.get(match.home_team_id)),
        away_team=team_out(teams.get(match.away_team_id)),
        score=ScoreOut(
            home=match.home_score,
            away=match.away_score,
            penalties_home=match.penalties_home,
            penalties_away=match.penalties_away,
            duration=match.duration,
        ),
        winner_team_id=match.winner_team_id,
    )
