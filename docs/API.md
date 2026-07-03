# API Reference

**Base URL (local):** `http://localhost:8006/api/v1`
**Base URL (production):** `https://worldcup.buenalynch.com/api/v1`

**Interactive Documentation:** When running the backend, visit [http://localhost:8006/docs](http://localhost:8006/docs) for Swagger UI with live API testing.

---

## Overview

worldcup is a **public read-only API**. There is no authentication, no user accounts, and no admin panel integration — by design. The frontend reads tournament data that the backend syncs hourly from football-data.org.

**Current Status:** 5 endpoints across 4 domains (planned — built in Phases 1 and 2)

**Deployment:** This API runs as a Docker container on `cepelynvault`, exposed via Cloudflare Tunnel at `worldcup.buenalynch.com`. See [SERVER-INFRASTRUCTURE.md](SERVER-INFRASTRUCTURE.md) for the full traffic flow.

---

## Table of Contents

1. [Health](#health) - Health check
2. [Groups](#groups-apiv1groups) - Group standings + group matches
3. [Matches](#matches-apiv1matches) - All matches, filterable by stage
4. [Bracket](#bracket-apiv1bracket) - Knockout structure for the radial view
5. [Meta](#meta-apiv1meta) - Sync status

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
| `home_score` | integer nullable | full-time (plus extra time/penalties noted in `duration`) |
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
