"""Shared ORM → schema serializers used by the routers."""

from app.models import Match, Scorer, Team
from app.schemas import MatchOut, ScoreOut, ScorerOut, TeamOut


def team_out(team: Team | None) -> TeamOut | None:
    if team is None:
        return None
    return TeamOut(id=team.id, name=team.name, tla=team.tla, crest_url=team.crest_url)


def scorer_out(scorer: Scorer, teams: dict[int, Team]) -> ScorerOut:
    team = teams.get(scorer.team_id)
    return ScorerOut(
        player_id=scorer.player_id,
        player_name=scorer.player_name,
        nationality=scorer.nationality,
        team_id=scorer.team_id,
        team_tla=team.tla if team else None,
        team_crest=team.crest_url if team else None,
        goals=scorer.goals,
        assists=scorer.assists,
        penalties=scorer.penalties,
        played_matches=scorer.played_matches,
    )


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
