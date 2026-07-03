# API Reference

**Base URL (local):** `http://localhost:8006/api/v1`
**Base URL (production):** `https://worldcup.buenalynch.com/api/v1`

**Interactive Documentation:** When running the backend, visit [http://localhost:8006/docs](http://localhost:8006/docs) for Swagger UI with live API testing.

---

## Overview

worldcup is a **public read-only API**. There is no authentication, no user accounts, and no admin panel integration — by design. The frontend reads tournament data that the backend syncs hourly from football-data.org.

**Current Status:** 8 endpoints across 6 domains

**Deployment:** This API runs as a Docker container on `cepelynvault`, exposed via Cloudflare Tunnel at `worldcup.buenalynch.com`. See [SERVER-INFRASTRUCTURE.md](SERVER-INFRASTRUCTURE.md) for the full traffic flow.

---

## Table of Contents

1. [Health](#health) - Health check
2. [Groups](#groups-apiv1groups) - Group standings + group matches
3. [Matches](#matches-apiv1matches) - All matches, filterable by stage
4. [Bracket](#bracket-apiv1bracket) - Knockout structure for the radial view
5. [Meta](#meta-apiv1meta) - Sync status
6. [Teams](#teams-apiv1teams) - Team picker list + single-team detail (My Team tab)
7. [Stats](#stats-apiv1stats) - Tournament-wide numbers (Cup Numbers tab)

---

## Health

System health check.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET`  | `/health` | Health check endpoint | Public |

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

## Groups (`/api/v1/groups`)

Group-phase standings and matches, shaped for the swipeable group cards.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET`  | `/groups` | All groups with standings and their matches | Public |

**Example response (truncated):**
```json
[
  {
    "name": "A",
    "standings": [
      {
        "position": 1,
        "team": { "id": 1, "name": "Mexico", "tla": "MEX", "crest_url": "..." },
        "played": 3, "won": 2, "drawn": 1, "lost": 0,
        "goals_for": 5, "goals_against": 2, "goal_difference": 3, "points": 7
      }
    ],
    "matches": [
      {
        "id": 101,
        "utc_date": "2026-06-11T20:00:00Z",
        "status": "FINISHED",
        "home_team": { "id": 1, "name": "Mexico", "tla": "MEX" },
        "away_team": { "id": 2, "name": "...", "tla": "..." },
        "score": { "home": 2, "away": 1 }
      }
    ]
  }
]
```

---

## Matches (`/api/v1/matches`)

All tournament matches.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET`  | `/matches` | List matches. Query params: `?stage=` (GROUP_STAGE, LAST_32, LAST_16, QUARTER_FINALS, SEMI_FINALS, THIRD_PLACE, FINAL), `?status=` (SCHEDULED, LIVE, FINISHED) | Public |

---

## Bracket (`/api/v1/bracket`)

Knockout matches structured by round, ordered for the radial layout (teams on the outside, rounds advancing inward, final at the center).

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET`  | `/bracket` | Knockout rounds with team slots, scores, and winners | Public |

**Example response (truncated):**
```json
{
  "rounds": [
    {
      "stage": "LAST_32",
      "matches": [
        {
          "id": 201,
          "position": 0,
          "home_team": { "id": 5, "name": "France", "tla": "FRA" },
          "away_team": { "id": 9, "name": "...", "tla": "..." },
          "score": { "home": null, "away": null },
          "status": "SCHEDULED",
          "winner_team_id": null,
          "feeds_into_match_id": 301
        }
      ]
    }
  ],
  "third_place": { "...": "MatchOut shape, or null" },
  "champion_team_id": null
}
```

`position` is the match's index within its round, in bracket order — the frontend maps it to an angle on the circle. `feeds_into_match_id` links each match to the next round inward. Because football-data.org exposes no bracket adjacency, links are derived from winners (exact once a match is decided) with ID-order fallback for unresolved rounds — see [research/football-data-analysis.md](research/football-data-analysis.md) §5. `THIRD_PLACE` sits outside `rounds` in its own field.

Score fields include `duration` (`REGULAR` / `EXTRA_TIME` / `PENALTY_SHOOTOUT`) and `penalties_home`/`penalties_away` when a shootout happened.

---

## Meta (`/api/v1/meta`)

Sync status, for the "last updated" indicator.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET`  | `/meta/last-sync` | Timestamp + result of the most recent football-data.org sync | Public |

**Response:**
```json
{
  "last_sync_at": "2026-07-03T14:00:12Z",
  "status": "success",
  "matches_updated": 3
}
```

---

## Teams (`/api/v1/teams`)

Powers the **My Team** tab: a picker over all teams plus a single-team detail view (standing, all matches, tournament scorers/assisters).

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET`  | `/teams` | All teams (id, name, tla, crest, `group_name`) for the picker | Public |
| `GET`  | `/teams/{team_id}` | One team's standing, all its matches, and its scorers. `404` if unknown | Public |

**`/teams/{team_id}` response (truncated):**
```json
{
  "team": { "id": 773, "name": "France", "tla": "FRA", "crest_url": "..." },
  "group_name": "I",
  "standing": {
    "position": 1, "team": { "...": "TeamOut" },
    "played": 3, "won": 3, "drawn": 0, "lost": 0,
    "goals_for": 7, "goals_against": 2, "goal_difference": 5, "points": 9
  },
  "matches": [ { "...": "MatchOut shape, chronological" } ],
  "scorers": [
    { "player_id": 3374, "player_name": "Kylian Mbappé", "nationality": "France",
      "goals": 6, "assists": 2, "penalties": null, "played_matches": 4 }
  ]
}
```

Each scorer also carries `team_id`, `team_tla`, and `team_crest` (the player's country, used for the flag + code shown in the Cup Numbers leaderboards). `standing` is `null` once a team leaves the group stage context. `scorers` are **tournament aggregates** from football-data.org's `/scorers` endpoint — the free tier exposes no per-match goal events, so we cannot attribute goals to specific matches. `assists`/`penalties` are populated where the provider supplies them (often `null`). The frontend derives form, summary stats, and the status badge from `matches`.

---

## Stats (`/api/v1/stats`)

Tournament-wide numbers for the **Cup Numbers** tab. All computed from data we already hold (matches + `scorers`) — no external calls.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET`  | `/stats` | Totals, top scorers, top assisters, and team/match superlatives | Public |

**Response (truncated):**
```json
{
  "totals": {
    "goals": 261, "matches_played": 85, "matches_total": 104,
    "goals_per_match": 3.07, "shootouts": 2, "extra_time": 1, "clean_sheets": 46
  },
  "top_scorers":   [ { "player_name": "Kylian Mbappé", "goals": 6, "assists": 2, "...": "ScorerOut" } ],
  "top_assisters": [ { "player_name": "Alexander Isak", "assists": 3, "...": "ScorerOut" } ],
  "superlatives": {
    "best_attack":       { "team": { "...": "TeamOut" }, "value": 14 },
    "best_defense":      { "team": { "...": "TeamOut" }, "value": 0 },
    "most_clean_sheets": { "team": { "...": "TeamOut" }, "value": 4 },
    "biggest_win":       { "match": { "...": "MatchOut" }, "value": 6 },
    "highest_scoring":   { "match": { "...": "MatchOut" }, "value": 9 }
  }
}
```

Team superlatives are aggregated across **all** matches (group + knockout), not just the group stage. `value` is goals/conceded/clean-sheet counts for team stats, and goal margin (`biggest_win`) or combined goals (`highest_scoring`) for match stats. Leaderboards are capped at 15 rows. Any superlative can be `null` before enough matches are played.

---

## Authentication

None. All endpoints are public and read-only. Do not add auth — see the project rules in CLAUDE.md.

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Invalid input (e.g. unknown stage filter)
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

---

## Pagination

Not needed — the full tournament is 104 matches and 48 teams. All list endpoints return complete collections.

---

## Future Endpoints (Planned)

See [PROGRESS.md](PROGRESS.md) for upcoming API features by phase.

---

## Database Schema

<!-- Keep this in sync with the SQLAlchemy models. -->

### `teams`
| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | football-data.org team id (not auto-increment — external id) |
| `name` | varchar(100) | e.g. "France" |
| `tla` | varchar(3) | three-letter code, e.g. FRA |
| `crest_url` | varchar(255) | flag/crest image URL from football-data.org |
| `group_name` | varchar(2) nullable | "A".."L" |

### `matches`
| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | football-data.org match id (external id) |
| `stage` | varchar(20) | GROUP_STAGE / LAST_32 / LAST_16 / QUARTER_FINALS / SEMI_FINALS / THIRD_PLACE / FINAL |
| `group_name` | varchar(2) nullable | set for group-stage matches |
| `utc_date` | timestamptz | kickoff, stored UTC |
| `status` | varchar(20) | SCHEDULED / TIMED / IN_PLAY / PAUSED / FINISHED |
| `home_team_id` | integer FK → teams.id, nullable | null until qualified |
| `away_team_id` | integer FK → teams.id, nullable | null until qualified |
| `home_score` | integer nullable | goals in play (regular + extra time). Shootout is **not** added here — it lives in `penalties_*`. `duration` says whether ET/pens happened |
| `away_score` | integer nullable | |
| `winner_team_id` | integer FK → teams.id, nullable | |
| `bracket_position` | integer nullable | index within its round, bracket order |
| `updated_at` | timestamptz | last sync touch |

### `group_standings`
| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | auto-increment |
| `group_name` | varchar(2) | "A".."L" |
| `team_id` | integer FK → teams.id | |
| `position` | integer | 1-4 |
| `played` / `won` / `drawn` / `lost` | integer | |
| `goals_for` / `goals_against` / `goal_difference` | integer | |
| `points` | integer | |
| `updated_at` | timestamptz | last sync touch |

### `scorers`
| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | auto-increment |
| `player_id` | integer | football-data.org player id (external) |
| `player_name` | varchar(120) | |
| `nationality` | varchar(60) nullable | |
| `team_id` | integer FK → teams.id | |
| `goals` | integer | tournament total to date |
| `assists` | integer nullable | provider-dependent, often null |
| `penalties` | integer nullable | provider-dependent |
| `played_matches` | integer nullable | |

Rebuilt in full each sync (like `group_standings`). Top ~100 scorers competition-wide; a team's list is the subset with `team_id = {id}`.

### `sync_runs`
| Column | Type | Notes |
|--------|------|-------|
| `id` | integer PK | auto-increment |
| `started_at` | timestamptz | |
| `finished_at` | timestamptz nullable | |
| `status` | varchar(20) | success / error |
| `detail` | text nullable | error message or summary |
| `matches_updated` | integer | |

---

**Last Updated:** 2026-07-03
**API Version:** v1
