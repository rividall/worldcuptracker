# football-data.org v4 API Integration Analysis

**Date:** 2026-07-03
**Analyzed:** [football-data.org](https://www.football-data.org) REST API v4 (external API, not a package — same analysis treatment)
**License:** Free tier (personal token), 10 requests/minute
**For:** Phase 1 — Data foundation

---

## Executive Summary

**Recommendation:** YES — sole data source for the app.

The v4 API covers the 2026 World Cup completely (competition code `WC`, season 2026): group standings for all 12 groups and all 104 matches including the full knockout tree. Verified live on 2026-07-03 with the project's token. The free tier's 10 req/min limit is irrelevant at our 2 requests/hour sync cadence. The one real limitation: the API does not expose explicit bracket adjacency (which R32 match feeds which R16 match), so bracket structure must be derived (see §5).

---

## 1. Endpoints Used

Base URL: `https://api.football-data.org/v4`
Auth: HTTP header `X-Auth-Token: <token>` (env `FOOTBALL_DATA_API_KEY`)

| Endpoint | Purpose | Calls per sync |
|----------|---------|----------------|
| `GET /competitions/WC/standings` | Group tables A–L | 1 |
| `GET /competitions/WC/matches` | All 104 matches, all stages | 1 |

---

## 2. Verified Response Shapes (live probe 2026-07-03)

### Standings
```json
{
  "season": {"id": 2398, "startDate": "2026-06-11", "endDate": "2026-07-19"},
  "standings": [
    {
      "stage": "ALL", "type": "TOTAL", "group": "Group A",
      "table": [
        {
          "position": 1,
          "team": {"id": 769, "name": "Mexico", "tla": "MEX",
                   "crest": "https://crests.football-data.org/769.svg"},
          "playedGames": 3, "won": 3, "draw": 0, "lost": 0,
          "points": 9, "goalsFor": 6, "goalsAgainst": 2, "goalDifference": 4
        }
      ]
    }
  ]
}
```

### Matches
```json
{
  "matches": [
    {
      "id": 537417, "stage": "LAST_32", "group": null,
      "utcDate": "2026-06-28T19:00:00Z", "status": "FINISHED",
      "homeTeam": {"id": 774, "name": "South Africa", "tla": "RSA", "crest": "..."},
      "awayTeam": {"id": 828, "name": "Canada", "tla": "CAN", "crest": "..."},
      "score": {
        "winner": "AWAY_TEAM", "duration": "REGULAR",
        "fullTime": {"home": 0, "away": 1}, "halfTime": {"home": 0, "away": 0}
      },
      "lastUpdated": "2026-07-02T15:20:12Z"
    }
  ]
}
```

Facts verified against the live tournament:

- **Stages:** `GROUP_STAGE` (72), `LAST_32` (16), `LAST_16` (8), `QUARTER_FINALS` (4), `SEMI_FINALS` (2), `THIRD_PLACE` (1), `FINAL` (1) = 104 matches.
- **Statuses seen:** `FINISHED`, `TIMED`. Docs also define `SCHEDULED`, `IN_PLAY`, `PAUSED`, `POSTPONED`, `SUSPENDED`, `CANCELLED`. Treat `IN_PLAY`/`PAUSED` as live.
- **Group naming is inconsistent:** matches use `"GROUP_A"`, standings use `"Group A"`. Normalize both to the letter (`"A"`).
- **Unresolved knockout slots:** `homeTeam`/`awayTeam` objects present with all-null fields (`id: null`) until qualified. 11 of 32 knockout matches unresolved as of probe date.
- **Extra time / penalties:** `score.duration` ∈ `REGULAR` / `EXTRA_TIME` / `PENALTY_SHOOTOUT`; shootout adds `score.penalties: {home, away}`. `score.winner` (`HOME_TEAM`/`AWAY_TEAM`) is authoritative — use it, not the goal comparison.
- **Crests:** SVG URLs on `crests.football-data.org` — hotlink directly, don't proxy or store.

---

## 3. Rate Limits & Sync Design

Free tier: **10 requests/minute** (429 with `Retry-After` when exceeded). Our sync = 2 requests per run, hourly (`FETCH_INTERVAL_MINUTES=60`) → ~48 requests/day. Zero risk. Rules (also in CLAUDE.md): never call the API from request handlers; only the background sync task touches it; retry with backoff on failure.

---

## 4. Server Infrastructure Impact

None — no new container, port, or subdomain. Backend needs outbound HTTPS to `api.football-data.org` only.

---

## 5. Known Limitation: No Bracket Adjacency

The API does **not** say which match feeds which. Match IDs are *not* in bracket order (verified: R16 match 537377 receives winners of L32 matches 537423/537424, not an adjacent-ID pair).

**Derivation strategy (implemented in `app/services/bracket.py`):**
1. Primary — **link by winner**: if a finished match's `winner_team_id` appears as home/away in a later-round match, that's the feed link. Exact, and coverage grows as the tournament progresses.
2. Positions are assigned top-down from the FINAL (position 0): a parent at position *p* expects children at *2p* and *2p+1*; linked children take their slots, unlinked children fill remaining slots in **bracket-template order** (see below), falling back to ID order.
3. `THIRD_PLACE` is excluded from the tree (rendered as a satellite node).

**Bracket-template override (added 2026-07-03).** Winner-linking only reconstructs adjacency for rounds already *played*. For future rounds the API leaves teams null and exposes no adjacency, so we ordered by match id — which assumes id order == bracket order. That assumption is **false for the quarter-finals and the round-of-16 feeding them**: football-data numbers the two middle quarters into the wrong halves. Verified against the official 2026 bracket — QF `537384` (Brazil/Mexico quarter) and QF `537385` (Spain·Portugal / USA·Belgium quarter) are transposed, which would let Brazil meet Spain/France before the final. `bracket.BRACKET_ORDER` pins the correct slot order for just `LAST_16` and `QUARTER_FINALS`; every other round is already id-ordered. Result: Brazil & Argentina occupy one half, Spain & France the other. If a future re-sync changes these knockout match ids, update `BRACKET_ORDER`.

Consequence: bracket geometry for fully-unresolved future rounds now follows the fixed template (correct halves) and self-corrects via winner-linking as rounds resolve.

---

## 6. Alternatives Considered

| Source | Verdict |
|--------|---------|
| **football-data.org** | ✅ Free, covers WC 2026 fully, clean JSON, generous enough limits for hourly sync |
| API-Football (api-sports.io) | Richer (lineups, events) but 100 req/day free cap and heavier integration — overkill for scores + standings |
| Scraping (FIFA site) | Fragile, ToS-risky, no stable contract — no |

---

## 7. Conclusion

Use football-data.org v4 as the single source. Two endpoints, hourly, upserted into Postgres; the app serves everything from its own DB. The only engineering of note is bracket-adjacency derivation, documented above and unit-tested.

*Compiled by: Claude (live API probe with project token)*
*Confidence: High — shapes verified against the running tournament*
