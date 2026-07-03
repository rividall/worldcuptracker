# worldcup -- Claude Code Instructions

## Before ANY Task

Read these docs in order before writing code:

1. **README.md** -- Tech stack, project structure, architecture, doc update checklist
2. **docs/SERVER-INFRASTRUCTURE.md** -- This app's ports, subdomain, container names. **Read this before making ANY deployment, networking, or Docker decision.**
3. **docs/TODO.md** -- Known issues & technical notes 
4. **docs/PROGRESS.md** -- What's built, what's in progress
5. **docs/research/RESEARCH.md** -- Index of all research, analysis & deployment docs

For feature-specific context, check the relevant docs linked from RESEARCH.md.

## Rules

- **Read official docs first.** Before using any package, library, or tool -- read its official documentation. Not your training data, not your memory. The actual docs.
- **docs/TODO.md is where all todos live.** Update all TODOS and keep theme here to work on them after finishing a main task.
- **Follow STYLEGUIDE.md** for all UI changes -- colors, typography, component patterns.
- **Follow API.md conventions** for all endpoint changes.
- **New package?** Follow the 3-stage pipeline in docs/research/RESEARCH.md: Research -> Analysis doc -> Deployment doc.
- **Do NOT run git commands** (commit, push, etc.) unless the user explicitly asks.

### Server & Deployment Rules

- **Use Makefile targets** for all container operations. `make dev` for local development, `make rebuild` after backend changes, `make deploy` on the server. Run `make help` to see all targets. Do not use raw `docker compose` commands unless the Makefile doesn't cover the use case.
- **No reverse proxy in containers.** Cloudflare Tunnel handles all ingress. Do NOT add nginx/Caddy/Traefik in front of services. See SERVER-INFRASTRUCTURE.md for the traffic flow.
- **No SSL certificates.** Cloudflare terminates TLS at the edge. Do NOT install certbot, Let's Encrypt, or generate local certs.
- **No exposed ports to the internet.** All web traffic goes through Cloudflare Tunnels. The only exception is Minecraft (port 25565). New services get a subdomain + tunnel ingress rule, never a port forward.
- **New subdomain = 3 steps.** (1) Add CNAME in Cloudflare DNS pointing to tunnel UUID, (2) Add ingress rule in `/etc/cloudflared/config.yml`, (3) Restart cloudflared. Document the chosen port in SERVER-INFRASTRUCTURE.md.
- **Pick a port that doesn't conflict.** Before assigning a port to a new service, check docs/SERVER-INFRASTRUCTURE.md for ports already in use.
- **Docker Compose per project.** Each project gets its own `docker-compose.yml` in its repo root. Shared infrastructure (tunnels, Pi-hole, Uptime Kuma) is documented but not managed by project compose files.

### Project-Specific Rules

- **No auth, by design.** This is a public read-only scoreboard. Do not add users, logins, JWT flows, or admin panel integration. The auth helpers in `app/core/security.py` are scaffold leftovers — leave them unused.
- **The frontend never calls football-data.org.** All external data flows through the backend sync service into Postgres. The frontend only reads from our own `/api/v1/` endpoints.
- **Respect the rate limit.** football-data.org free tier = 10 requests/minute. Sync runs hourly via the lifespan background task (2-3 requests per run). Never fetch external data inside a request handler.
- **The bracket is derived, not stored.** Compute knockout structure from `matches` (stage + winner). No separate bracket table.
- **Timezones: store UTC, render in a viewer-selected zone (default Spain).** Match kickoff times are stored as timestamptz. The frontend renders them in a zone the viewer picks via the header timezone picker (Spain / Chile / their own device zone), persisted in `localStorage` (`worldcup.timezone`), default Spain. Zone registry + formatter factory live in `frontend/src/lib/time.ts`; the selected zone flows through `frontend/src/lib/timezone.tsx` (`TimeZoneProvider` / `useKickoffFormatter`). The zone name (e.g. GMT+2) is always shown so times aren't misread. To add a zone, append to `TIME_ZONES` in `time.ts`.
- **Mobile-first.** The group swipe and the radial bracket are the core interactions and must work well on a phone (test at 375px width). Swipe must be touch-native (pointer events), with arrow-key support on desktop.
- **The radial bracket is hand-rolled SVG.** Positions are computed from match data (polar coordinates, rounds advancing inward). Do not pull in a charting/bracket library without an analysis doc in docs/research/ first.
- **The tournament is live NOW.** The 2026 World Cup runs June 11 – July 19, 2026. Prefer shipping something working today over polishing. Phase 1 before beauty.

## After Completing a Feature

Follow the 7-step doc update checklist in README.md:

1. **README.md** -- Tech Stack, Project Structure, Architecture Notes, Development Progress
2. **PROGRESS.md** -- Check off completed items
3. **TODO.md** -- When finding TODOs already completed
4. **API.md** -- If endpoints were added, changed, or removed
5. **SERVER-INFRASTRUCTURE.md** -- If ports, subdomains, containers, or tunnel config changed
6. **docs/research/RESEARCH.md** -- If new analysis or deployment docs were created
7. **Relevant deployment doc** in docs/research/ -- Update status, known issues

This is not optional. Do it before considering a feature "done".
