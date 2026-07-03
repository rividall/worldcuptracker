export interface Team {
  id: number;
  name: string;
  tla: string | null;
  crest_url: string | null;
}

export interface Score {
  home: number | null;
  away: number | null;
  penalties_home: number | null;
  penalties_away: number | null;
  duration: string;
}

export interface Match {
  id: number;
  stage: string;
  group_name: string | null;
  utc_date: string;
  status: string;
  home_team: Team | null;
  away_team: Team | null;
  score: Score;
  winner_team_id: number | null;
}

export interface Standing {
  position: number;
  team: Team;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
}

export interface Group {
  name: string;
  standings: Standing[];
  matches: Match[];
}

export interface BracketMatch extends Match {
  position: number;
  feeds_into_match_id: number | null;
}

export interface Round {
  stage: string;
  matches: BracketMatch[];
}

export interface Bracket {
  rounds: Round[];
  third_place: Match | null;
  champion_team_id: number | null;
}

export interface LastSync {
  last_sync_at: string | null;
  status: string | null;
  matches_updated: number | null;
  detail: string | null;
}

export const LIVE_STATUSES = ["IN_PLAY", "PAUSED", "LIVE"];

export function isLive(match: Match): boolean {
  return LIVE_STATUSES.includes(match.status);
}
