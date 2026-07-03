# Implementation Progress

Multi-phase build plan for worldcup. Each phase produces a runnable increment. ALL DEVELOPMENT MUST CONFORM WITH THE RELATED LIBRARIES AND DATABASE SCHEMES. ALWAYS SEARCH FOR THE PROPER DOCUMENTATION OF LIBRARIES AND READ THEM TO MAKE SURE THE CODE CONFORMS TO WHAT THE LIBRARIES EXPECT.

---

## Phase 1: Data foundation + Group phase **COMPLETE**

### Backend
- [x] Research football-data.org v4 API (endpoints for WC 2026: `/competitions/WC/standings`, `/competitions/WC/matches`, auth header `X-Auth-Token`, rate limits) — create `docs/research/football-data-analysis.md`
- [x] Models + Alembic migration: `teams`, `matches`, `group_standings`, `sync_runs` (see schema in API.md)
- [x] Sync service (`app/services/sync.py`): fetch standings + matches via httpx, upsert into DB, record a `sync_runs` row; tolerant of partial data (knockout teams TBD)
- [x] Hourly background task in FastAPI lifespan calling the sync service every `FETCH_INTERVAL_MINUTES` (default 60); run once on startup
- [x] Endpoints: `GET /api/v1/groups`, `GET /api/v1/matches`, `GET /api/v1/meta/last-sync` (see API.md)
- [x] Tests: bracket derivation (5 unit tests) + endpoint tests on seeded SQLite (11 passing); sync verified end-to-end against the live API

### Frontend
- [x] App shell: two tabs (Group phase / Elimination phase), dark theme per STYLEGUIDE.md
- [x] Group card: standings table (pos, team, P W D L GD Pts) + that group's matches with scores/kickoff times
- [x] Swipe navigation between groups: touch/pointer gestures + arrow keys, with group indicator dots (A–L)
- [x] Data layer: fetch from `/api/v1/groups`, poll every 15 min while tab is visible
- [x] Elimination tab placeholder — superseded: real bracket shipped with Phase 2 in the same build

---

## Phase 2: Radial elimination bracket **COMPLETE**

### Backend
- [x] `GET /api/v1/bracket` — knockout matches grouped by round (LAST_32 → FINAL), each with `bracket_position` and `feeds_into_match_id` so the frontend can lay out the circle (see API.md)
- [x] Bracket-order logic: derive `bracket_position` and feed links from football-data.org match data

### Frontend
- [x] RadialBracket SVG component: 32 first-round slots around the circumference, rounds advancing inward, trophy at the center (reference image in project brief)
- [x] Polar layout math: angle per bracket position, radius per round; connector lines between a match and the match it feeds into
- [x] Team nodes: crest/flag images, dimmed when eliminated, winner's path highlighted toward the center
- [x] Tap/click a node → match detail popover (score, status, kickoff time)
- [x] Responsive: scales down to 375px wide (pinch/scroll if needed), works with touch

---

## Phase 3: Auto-update polish + live feel **COMPLETE** (optional item deferred)

### Backend
- [x] Sync hardening: retry with backoff, respect 10 req/min limit, log failures to `sync_runs`
- [ ] Optional (deferred): shorten sync interval during live-match windows (check scheduled kickoffs)

### Frontend
- [x] "Last updated X min ago" indicator fed by `/api/v1/meta/last-sync`
- [x] LIVE badge on in-play matches; auto-refresh UI when a poll returns new data
- [x] Empty/loading/error states polished

---

## Phase 4: My Team + timezone picker **COMPLETE** (2026-07-03)

### Backend
- [x] `scorers` model + migration `0002` (player, team, goals, assists, penalties, played) — rebuilt each sync
- [x] Sync step `_sync_scorers` pulls `/competitions/WC/scorers?limit=100` (3rd request/run, still trivial vs the limit)
- [x] `GET /api/v1/teams` (picker list) and `GET /api/v1/teams/{id}` (standing + all matches + scorers); `404` on unknown team
- [x] Tests still green (11 passing)

### Frontend
- [x] **My Team** tab: team picker (grouped by group A–L), remembered in `localStorage` (`worldcup.myteam`)
- [x] Team page: identity header + status badge, next match, group standing, summary stats, recent form, full match list (team perspective), scorers/assisters table — all in the selected timezone
- [x] **Timezone picker** in the header (Spain / Chile / device zone), remembered in `localStorage` (`worldcup.timezone`); `lib/time.ts` + `lib/timezone.tsx`

### Cup Numbers tab (added same phase)
- [x] `GET /api/v1/stats` — tournament totals (goals, goals/match, matches played/total, shootouts, extra-time, clean sheets), top scorers, top assisters, and superlatives (best attack/defense, most clean sheets, biggest win, highest-scoring match). All computed from matches + `scorers`; no new external calls.
- [x] **Cup Numbers** tab: totals stat grid, superlative cards, scorers + assists leaderboards.

### Known limits
- Scorers are tournament aggregates (no per-match goal events on the free tier); assists/penalties populated where the provider supplies them.
- No cards / saves / possession / xG (not available on the free tier), so those stats are out of scope.

---

## Deployment Phase: Server Setup **COMPLETE** (2026-07-03) — live at worldcup.buenalynch.com

This phase takes the project from "works on localhost" to "running on the server behind a subdomain." Read [SERVER-INFRASTRUCTURE.md](SERVER-INFRASTRUCTURE.md) before starting.

### Pre-flight Checks
- [ ] Read SERVER-INFRASTRUCTURE.md to understand the current server topology
- [ ] Port check done at scaffold time: 3007 (frontend) / 8006 (backend) were next available per the central port map
- [ ] Subdomain decided: `worldcup.buenalynch.com`

### Docker
- [ ] docker-compose.yml: all services (backend, frontend, database)
- [ ] .env with real values (`FOOTBALL_DATA_API_KEY`, `SECRET_KEY`, ports)
- [ ] Docker volumes for persistent data (`pgdata`, `uploads`)
- [ ] Remove the `db` host port mapping in production (postgres internal only)
- [ ] Test full stack locally with `sudo docker compose up`

### Cloudflare Tunnel & DNS
- [ ] Add CNAME record in Cloudflare DNS: `worldcup.buenalynch.com` → tunnel UUID
- [ ] Add ingress rule in `/etc/cloudflared/config.yml` on cepelynvault:
  ```yaml
  - hostname: worldcup.buenalynch.com
    service: http://localhost:3007
  ```
- [ ] Restart cloudflared: `sudo systemctl restart cloudflared`
- [ ] Verify subdomain resolves and reaches the service

### Monitoring
- [ ] Add HTTP monitor in Uptime Kuma (uptime.buenalynch.com) for worldcup.buenalynch.com

### Documentation
- [ ] Update SERVER-INFRASTRUCTURE.md: add container entry, port, subdomain, tunnel ingress
- [ ] Update central `_lynchProtocol/SERVER-INFRASTRUCTURE.md` port map + tunnel config in the parent workspace
- [ ] Update README.md: fill in the Server & Deployment table
- [ ] Create docs/research/worldcup-deployment.md with setup steps, troubleshooting, and rollback instructions

<!--
  This deployment phase template covers the standard path for all home projects:
  Docker Compose → Cloudflare Tunnel → monitoring → docs.

  If the project has special networking needs (e.g., WebSocket, UDP, port forwarding
  like Minecraft), document those exceptions here and in SERVER-INFRASTRUCTURE.md.
-->
