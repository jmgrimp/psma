# PSMA (Program Subscription Manager Application)

## Documentation

- Start here (business + technical): [docs/README.md](docs/README.md)
- Technical index: [docs/technical/README.md](docs/technical/README.md)
- Business index: [docs/business/README.md](docs/business/README.md)

## Repository Layout

- `apps/api` — FastAPI backend (Python + `uv`)
- `apps/web` — Next.js frontend (Node + pnpm)
- `packages/api-client` — generated API client/types (OpenAPI → TS)
- `contracts/` — versionable contracts (OpenAPI + JSON Schemas + registries)

## Development (Full Setup)

### Prereqs

- Node.js >= 20.9 (recommended: use `.nvmrc` / `.node-version`)
- pnpm (via Corepack)
- `uv` for Python dependency management

Ports used by default:
- API: `http://localhost:8000`
- Web: `http://localhost:3000`

Recommended installs:

- Node via nvm:
	- `nvm install && nvm use`
- pnpm via Corepack:
	- `corepack enable && corepack prepare pnpm@9.15.4 --activate`
- `uv` (macOS/Linux):
	- `curl -LsSf https://astral.sh/uv/install.sh | sh`
	- Add to PATH for new shells:
		- `source $HOME/.local/bin/env`

### Install

1) Install Node dependencies (repo root):
- `pnpm install`

2) Install Python dependencies (API):
- `cd apps/api && uv sync --dev`

### Environment

Web:
- Copy [apps/web/.env.local.example](apps/web/.env.local.example) → `apps/web/.env.local`
- Set `NEXT_PUBLIC_API_BASE_URL` (defaults to `http://localhost:8000`)

API:
- Copy `apps/api/.env.example` → `apps/api/.env`
- Set `PSMA_TMDB_API_KEY` to enable TMDB endpoints

### Run (dev)

In two terminals from repo root:

- `pnpm dev:api` (FastAPI on `http://localhost:8000`)
- `pnpm dev:web` (Next.js on `http://localhost:3000`)

API docs (Swagger UI):

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

Docker is intentionally not required for MVP.

Alternatively, run both with:

- `./scripts/dev.sh`

### Verify it's working

Backend:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Frontend smoke pages:
- `http://localhost:3000/smoke/providers`
- `http://localhost:3000/smoke/interactive`

### Generate API types

Generate OpenAPI + TypeScript client/types:
- `pnpm gen:api`

Generate just OpenAPI:
- `pnpm gen:openapi`

## Provider API quick test (dev)

PSMA currently includes two “free-first” provider integrations you can exercise via Swagger.

### TVmaze (no key required)

- Search shows: `GET /providers/tvmaze/search/shows?q=girls`
- Fetch show details: `GET /providers/tvmaze/shows/{show_id}?embed=episodes`

Note: TVmaze data is licensed CC BY-SA. If we display this data in-app, we must attribute TVmaze and comply with ShareAlike.

### TMDB (API key required)

1) Set `PSMA_TMDB_API_KEY` in `apps/api/.env` (see `apps/api/.env.example`)
2) Restart the API

- Search TV: `GET /providers/tmdb/search/tv?query=Breaking+Bad`
- Watch providers: `GET /providers/tmdb/tv/{series_id}/watch/providers?country=US`

Note: TMDB watch-provider data requires JustWatch attribution (per TMDB docs). Our API returns an `attribution` field on the watch-provider endpoint.

## Troubleshooting

- If Next.js refuses to start due to Node version, ensure Node >= 20.9 (then `nvm use`) and retry.
- If `uv` is not found after installing, run `source $HOME/.local/bin/env` (and add it to your shell profile).
- If TMDB endpoints return HTTP 503, verify `PSMA_TMDB_API_KEY` is set in `apps/api/.env` and restart `pnpm dev:api`.
- If ports are in use, stop the conflicting process or change ports in your run command.

## Lint and tests

API:
- Tests: `cd apps/api && uv run pytest -q`
- Lint: `cd apps/api && uv run ruff check`

Web:
- Lint: `pnpm -C apps/web lint`
