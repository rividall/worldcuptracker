# worldcup -- Server Infrastructure

Last updated: 2026-07-03

## Machine

- **Server**: cepelynvault
- **Tunnel**: buenalynch (mini PC)

## This App

| Service | Port | Container |
|---------|------|-----------|
| Frontend | 3007 | worldcup-frontend |
| Backend | 8006 | worldcup-backend |
| Database | 5432 (internal only, no host port) | worldcup-db |

<!-- Add rows as your stack grows (Redis, worker, etc.) -->

- **Subdomain**: worldcup.buenalynch.com
- **Compose file**: `~/repositories/worldcup/docker-compose.yml`
- **Volumes**: `pgdata` (postgres data), `uploads`

## Notes

Port assignments are managed centrally by the lynch-project-scaffolder skill. If you need to check what other ports are in use across all projects, refer to `_lynchProtocol/SERVER-INFRASTRUCTURE.md` in the parent workspace (not accessible from within this repo).

The backend needs outbound HTTPS to api.football-data.org for the hourly sync (outbound traffic works normally through the tunnel setup; nothing to configure).
