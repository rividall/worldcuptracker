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

export interface TeamListItem extends Team {
  group_name: string | null;
}

export interface Scorer {
  player_id: number;
  player_name: string;
  nationality: string | null;
  team_id: number | null;
  team_tla: string | null;
  team_crest: string | null;
  goals: number;
  assists: number | null;
  penalties: number | null;
  played_matches: number | null;
}

export interface TeamDetail {
  team: Team;
  group_name: string | null;
  standing: Standing | null;
  matches: Match[];
  scorers: Scorer[];
}

export interface TournamentTotals {
  goals: number;
  matches_played: number;
  matches_total: number;
  goals_per_match: number;
  shootouts: number;
  extra_time: number;
  clean_sheets: number;
}

export interface StatTeam {
  team: Team;
  value: number;
}

export interface StatMatch {
  match: Match;
  value: number;
}

export interface Superlatives {
  best_attack: StatTeam | null;
  best_defense: StatTeam | null;
  most_clean_sheets: StatTeam | null;
  biggest_win: StatMatch | null;
  highest_scoring: StatMatch | null;
}

export interface CupNumbers {
  totals: TournamentTotals;
  top_scorers: Scorer[];
  top_assisters: Scorer[];
  superlatives: Superlatives;
}

export const LIVE_STATUSES = ["IN_PLAY", "PAUSED", "LIVE"];

export function isLive(match: Match): boolean {
  return LIVE_STATUSES.includes(match.status);
}

export const FINISHED_STATUS = "FINISHED";
