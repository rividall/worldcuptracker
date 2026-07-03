# worldcup

Follow the 2026 FIFA World Cup: swipeable group standings and a radial knockout bracket where winners advance inward toward the trophy at the center. Match results auto-sync hourly from football-data.org.

## Tech Stack

| Layer       | Technology                                              |
| ----------- | ------------------------------------------------------- |
| Backend     | FastAPI (Python 3.11) + SQLAlchemy 2 (async) + Alembic  |
| Frontend    | React 18 + TypeScript + Vite                            |
| State       | React state/context (no external state lib yet)         |
| Auth        | None — public read-only app                             |
| Database    | PostgreSQL 16 (Docker, internal only)                   |
| Data source | football-data.org API (competition `WC`, hourly sync)   |
| Deploy      | Docker Compose on cepelynvault + Cloudflare Tunnel      |

<!--
  Add rows as your stack grows. Examples:
  | i18n        | react-i18next (10 EU languages)                         |
  | Messaging   | Matrix/Synapse (self-hosted homeserver)                  |
  | Backups     | prodrigestivill/postgres-backup-local (Docker sidecar)   |
-->

## Server & Deployment

This project runs on the home server infrastructure documented in [docs/SERVER-INFRASTRUCTURE.md](docs/SERVER-INFRASTRUCTURE.md). Key deployment facts:

| Setting               | Value                                          |
| --------------------- | ---------------------------------------------- |
| Host machine          | `cepelynvault`                                 |
| Subdomain             | worldcup.buenalynch.com                        |
| Container port        | 3007 (frontend), 8006 (backend)                |
| Tunnel                | `buenalynch` (mini PC)                         |
| Compose file          | `./docker-compose.yml`                         |
| Data volumes          | `pgdata` (postgres data), `uploads`            |

**How traffic reaches this service:**
```
User browser
  → worldcup.buenalynch.com (Cloudflare DNS, CNAME → tunnel UUID)
  → Cloudflare edge (TLS termination)
  → Tunnel to cepelynvault
  → cloudflared forwards to localhost:3007
  → Docker container serves the response
```

## Project Structure

```
worldcup/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, health endpoint, lifespan (migrations + hourly sync)
│   │   ├── core/              # config, database, security helpers
│   │   ├── models/            # SQLAlchemy models (teams, matches, standings, scorers, sync_runs)
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # groups, matches, bracket, meta, teams, stats
│   │   └── services/          # football-data.org fetcher + sync scheduler
│   ├── alembic/               # migrations
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/client.ts      # typed fetch wrapper
│   │   ├── components/        # GroupCard, RadialBracket, TabBar, TimezonePicker, ...
│   │   ├── lib/               # time zones (time.ts) + timezone context (timezone.tsx)
│   │   ├── pages/             # GroupPhase, EliminationPhase, MyTeam, CupNumbers
│   │   └── App.tsx
│   ├── nginx.conf             # SPA fallback + /api proxy to backend
│   └── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env.example
├── docs/
│   ├── SERVER-INFRASTRUCTURE.md  # This app's ports, subdomain, containers
│   ├── API.md                    # Complete API endpoint reference
│   ├── TODO.md                   # Future features & pending tasks
│   ├── PROGRESS.md               # Implementation progress checklist
│   ├── STYLEGUIDE.md             # Visual design cheatsheet
│   └── research/                 # Package research, analysis & deployment guides
└── ...
```

<!--
  Keep this tree updated as the project grows. This is the map.
  Anyone reading the project for the first time will use this to orient themselves.
-->

## Architecture Notes

- **Backend pattern**: Routers → Services → Models. Routers handle HTTP, services contain business logic (including the football-data.org fetcher), models define the schema.
- **Data flow**: A background task in the FastAPI lifespan calls the sync service every `FETCH_INTERVAL_MINUTES` (default 60). The sync service pulls standings and fixtures/results from football-data.org (competition `WC`), upserts into Postgres, and records a row in `sync_runs`. The frontend only ever talks to our own API — never to football-data.org directly.
- **Rate limits**: football-data.org free tier allows 10 requests/minute. The hourly sync uses 2-3 requests per run. Never fetch from the external API in request handlers.
- **Bracket is derived**: knockout structure is computed from `matches` rows (stage + winner), not stored as a separate entity.
- **No auth**: this is a public scoreboard. There are no users, logins, or admin panel hooks.
- **Database**: Production uses local `postgres:16-alpine` Docker container, internal only (no host port on the server).
- **API**: All routes under `/api/v1/`.
- **Deployment**: Docker Compose on cepelynvault, exposed via Cloudflare Tunnel. No reverse proxy in front, no local SSL.

## API Documentation

**Current Status:** 8 endpoints across 6 domains (groups, matches, bracket, meta, teams, stats) + health — all implemented

**Resources:**
- [API Reference](docs/API.md) - Complete endpoint list with examples
- [Swagger UI](http://localhost:8006/docs) - Interactive docs (when backend is running)

<!--
  Update the endpoint/domain count as the API grows.
-->

## Development Progress

See [docs/PROGRESS.md](docs/PROGRESS.md) for the full implementation checklist.

**Current status**:
- ✅ **Phase 1 complete** -- football-data.org fetcher, hourly sync, Group phase tab with swipe
- ✅ **Phase 2 complete** -- Radial elimination bracket (SVG, trophy at center)
- ✅ **Phase 3 complete** -- Live badges, last-updated indicator, sync retries (live-window fast-sync deferred)
- ✅ **Deployed** -- Docker + Cloudflare Tunnel at worldcup.buenalynch.com
- ✅ **My Team tab** -- Team picker (localStorage-remembered) → standing, matches, form, summary stats, and tournament scorers/assisters (new `scorers` sync + `/api/v1/teams` endpoints)
- ✅ **Cup Numbers tab** -- Tournament-wide stats: totals (goals, goals/match, shootouts, extra-time, clean sheets), top scorers, top assists, and team/match superlatives (`/api/v1/stats`)
- ✅ **Timezone picker** -- Header picker (Spain / Chile / device zone), localStorage-remembered

## Documentation

All documentation starts on this README and lives in .md files for robustness. Your memory WILL fail, and AI WILL compress and forget certain stuff. That is why every step from research, architecture, structure, installation, development and deployment must absolutely live in the DOCS.

Before coding, read this and all documents. New library/package? Check docs/research/. New feature? Update PROGRESS.md and flag any open items to the user. Setup or deployment changes? Create or update a -deployment.md file in docs/research/. API change? Update API.md. UI changes? Follow STYLEGUIDE.md patterns. **Deploying to the server?** Read SERVER-INFRASTRUCTURE.md first.

- [SERVER-INFRASTRUCTURE.md](docs/SERVER-INFRASTRUCTURE.md) -- Server topology, tunnels, domains, containers, port map. **Read before any deployment decision.**
- [API.md](docs/API.md) -- Complete API endpoint reference
- [STYLEGUIDE.md](docs/STYLEGUIDE.md) -- Colors, typography, component patterns
- [PROGRESS.md](docs/PROGRESS.md) -- What's built, what's next. Go-to place to track all features developed and in development.
- [TODO.md](docs/TODO.md) -- Future features and pending tasks. All TODOs must be added here always, no questions asked, no "I will add it in a minute" excuses. We do not trust AI context. It gets shrunk at weird intervals, and we don't trust it retains all TODOs. So just document it there.
- [Package Research Guide](docs/research/RESEARCH.md) -- Index of all research, analysis & deployment docs. Explains the 3-stage pipeline (research -> analysis -> deployment) and how to evaluate packages for consistency and interoperability.
  - [Analysis docs](docs/research/) -- Package/Library specific docs generated using the above guide, rationale behind choosing the pack/lib.
  - [Deployment docs](docs/research/) -- Deployment instructions and bug/troubleshooting docs for any feature that has passed the Analysis stage.

### After deploying a feature, update docs in this order:

1. **README.md** -- Tech Stack table, Project Structure tree, Architecture Notes, Development Progress, Server & Deployment table
2. **[PROGRESS.md](docs/PROGRESS.md)** -- Check off completed items, add new sub-items if needed
3. **[TODO.md](docs/TODO.md)** -- when finding TODOs already completed.
4. **[API.md](docs/API.md)** -- If endpoints were added, changed, or removed
5. **[SERVER-INFRASTRUCTURE.md](docs/SERVER-INFRASTRUCTURE.md)** -- If ports, subdomains, containers, tunnel ingress rules, or cron jobs changed
6. **[docs/research/RESEARCH.md](docs/research/RESEARCH.md)** -- If new analysis or deployment docs were created, update the tables
7. **Relevant deployment doc** in docs/research/ -- Update status, add known issues, troubleshooting

This is not optional. Context gets compressed, memory gets lost, sessions end. The docs are the only thing that survives. Update them before you consider a feature "done".

PS: Remember the mantra: "Every piece of code created must conform to the documentation and libraries we are using. Creating code without first looking at the libraries doc pages on their repos is super risky, and leads to spaghettification of code. Unacceptable and totally avoidable. Always read the docs!"
