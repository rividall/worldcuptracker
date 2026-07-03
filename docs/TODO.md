# TODO - Future Features & Tasks

> Track pending features and tasks that are not part of the current phase roadmap.

For the reader, human or machine, know this: Memory is a beautiful, complex, amazing, and rather fragile thing. Don't stress yourself by overloading this precious gift from evolution with data that will not live on. Be true to yourself. All TODOs must absolutely completely quickly be added to this file.
Otherwise it will be forgotten during your sleep tonight, or during your next context compression.

Whenever visiting this page to look for info on how to perform a task, remember the mantra: "Every piece of code created must conform to the documentation and libraries we are using. Creating code without first looking at the libraries doc pages on their repos is stupid, and leads to spaghettification of code. Unacceptable and totally avoidable. Always read the docs! They usually are on the research/ folder."

---

## Pending

- [ ] **[UI] Settings page** -- Add a dedicated Settings page/route (reachable from the tab bar or a header gear icon) to hold user preferences. The timezone picker (done, see below) currently lives in the header; it could move here once there's more than one preference. Keep it lightweight and client-side (no auth, no backend — this is a public read-only app). Follow STYLEGUIDE.md for layout/controls.
- [ ] **[UI] Timezone picker — full IANA list** -- The picker ships with Spain (default), Chile, and "My timezone" (device zone). A searchable full IANA zone list is still open. Add zones by appending to `TIME_ZONES` in `frontend/src/lib/time.ts`.
- [ ] **[Security] Regenerate football-data.org token** -- The current token was pasted in a chat; regenerate it in the football-data.org user panel and update `.env` when convenient.
- [ ] **[DX] Commit frontend package-lock.json** -- Generated on first `npm install`; commit it so Docker builds are reproducible.
- [ ] **[UI] Third-place layout** -- Currently a compact card below the SVG. Revisit whether it should be a satellite node inside the radial view.
- [ ] **[Server] Add Uptime Kuma monitor** -- After deploy, add HTTP check for worldcup.buenalynch.com in Uptime Kuma (uptime.buenalynch.com).
- [ ] **[Tunnel] Update cloudflared ingress** -- After adding the subdomain, update `/etc/cloudflared/config.yml` on cepelynvault (hostname worldcup.buenalynch.com → localhost:3007) and restart cloudflared.
- [ ] **[Docker] Drop db host port in production** -- `docker-compose.yml` maps `DB_PORT` for local dev convenience; on the server, postgres should be internal only like every other project (remove or comment the `ports:` mapping on `db`).
---

## Done

- [x] **[API] Live-window fast sync** DONE (2026-07-04) -- Sync cadence is now dynamic: every `LIVE_FETCH_INTERVAL_MINUTES` (2) while any match is live or in its kickoff window, else hourly (`FETCH_INTERVAL_MINUTES`). `sync.py:_has_live_window` + `sync_loop`. Frontend polls in lockstep: `usePolling` accepts a data-derived interval, and GroupPhase / EliminationPhase / MyTeam poll every 45s (`LIVE_POLL_MS`) when a match is live, else 15 min (`IDLE_POLL_MS`); helpers `isLiveWindow`/`anyLive` in `api/types.ts`. 3 req/sync × every 2 min is far within the 10 req/min free tier.
- [x] **[Feature] Cup Numbers tab** DONE (2026-07-03) -- Tournament-wide stats tab. New `GET /api/v1/stats` (`app/routers/stats.py`) computes totals (goals, goals/match, shootouts, extra-time, clean sheets), top scorers, top assists, and superlatives (best attack/defense, most clean sheets, biggest win, highest-scoring match) from matches + `scorers` — no new external calls. Frontend page `pages/CupNumbers.tsx` + shared `components/Stat.tsx`. User chose Totals + Superlatives panels (Player spotlights / penalty breakdown declined). Cards/saves/possession/xG not possible on the free tier.
- [x] **[Feature] My Team tab** DONE (2026-07-03) -- Team picker (localStorage `worldcup.myteam`) → team detail: status badge, next match, group standing, summary stats, form, full match list, and tournament scorers/assisters. New backend: `scorers` table + migration `0002`, `/scorers` sync step (3rd request/run), `GET /api/v1/teams` + `/api/v1/teams/{id}`. Limitation: scorers are tournament aggregates only — the free tier exposes no per-match goal events (see football-data-analysis.md §1). A per-match scorer timeline would need a paid tier / different source.
- [x] **[UI] Timezone picker (Spain / Chile / device)** DONE (2026-07-03) -- Header `<select>` lets the viewer switch the display zone; persisted in `localStorage` (`worldcup.timezone`), default Spain. Zone registry in `frontend/src/lib/time.ts`, context + memoized formatter in `frontend/src/lib/timezone.tsx`, picker in `frontend/src/components/TimezonePicker.tsx`. Times stay stored UTC; only rendering changes. Full IANA-list picker + a dedicated Settings page remain in Pending.
- [x] **[Bug] Bracket halves swapped (Brazil could meet Spain/France before the final)** FIXED (2026-07-03) -- football-data match ids are in bracket order for every knockout round except the QFs and the R16 feeding them, where the two middle quarters are numbered into the wrong halves. The winner-link derivation can't catch this because those rounds aren't played yet, so it fell back to id order. Added `BRACKET_ORDER` in `app/services/bracket.py` pinning the true slot order for `LAST_16` + `QUARTER_FINALS` (swaps QF 537384 ↔ 537385 subtrees). Now Brazil & Argentina share one half, Spain & France the other. See football-data-analysis.md §5. NOTE: if a re-sync ever changes these knockout match ids, `BRACKET_ORDER` must be updated.
- [x] **[Bug] Sync failed with FK violation on every run** FIXED (2026-07-03) -- `run_sync` errored with `ForeignKeyViolationError: Key (team_id)=... not present in table "teams"` (raised via query-invoked autoflush), so nothing ever synced. Root cause: SQLAlchemy orders flush-time INSERTs by `relationship()` links, not bare `ForeignKey` columns, and we declare none between `GroupStanding`/`Match` and `Team`. An autoflush could emit the child row before its parent `teams` row. Fix: `await session.flush()` at the end of `_upsert_team` in `app/services/sync.py` so the parent row is persisted first. (Not the API — the token works and returns full WC data.)
- [x] **[API] Get football-data.org API key** DONE (2026-07-03) -- Key in `.env` as `FOOTBALL_DATA_API_KEY`, sent as `X-Auth-Token` header by `app/services/football_data.py`.
- [x] **[Infra] Time pressure** DONE (2026-07-03) -- All three phases built in one pass; only server deployment remains.

<!--
  Move completed items here with a date and brief note on how it was resolved.
  Format: - [x] **[Category] Short title** DONE (YYYY-MM-DD) -- Brief resolution note. Link to deployment doc if relevant.
  Examples:

  - [x] **[Infra] Automated backups** DONE (2026-03-06) -- Docker sidecar containers with daily schedule. See [postgres-backup-deployment.md](research/postgres-backup-deployment.md).
  - [x] **[Server] Subdomain for staging** DONE (2026-03-10) -- Added staging.buenalynch.com CNAME + tunnel ingress rule. Port 8090 on cepelynvault.
  - [x] **[UI] Notification overflow** FIXED (2026-03-04) -- Added PopoverPositioner wrapper in TopNav.tsx.
-->
