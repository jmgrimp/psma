# PSMA (Program Subscription Manager Application)

## Documentation

- Start here (business + technical): [docs/README.md](docs/README.md)
- Technical index: [docs/technical/README.md](docs/technical/README.md)
- Business index: [docs/business/README.md](docs/business/README.md)

## Development Quickstart

### Prereqs

- Node.js >= 20.9 (recommended: use `.nvmrc` / `.node-version`)
- pnpm (via Corepack)
- `uv` for Python dependency management

Recommended installs:

- Node via nvm:
	- `nvm install 20 && nvm use 20`
- pnpm via Corepack:
	- `corepack enable && corepack prepare pnpm@9.15.4 --activate`
- `uv` (macOS/Linux):
	- `curl -LsSf https://astral.sh/uv/install.sh | sh`
	- Add to PATH for new shells:
		- `source $HOME/.local/bin/env`

### Install

- `pnpm install`
- `cd apps/api && uv sync --dev`

### Environment

- Web: copy [apps/web/.env.local.example](apps/web/.env.local.example) → `apps/web/.env.local`
- API: copy `apps/api/.env.example` → `apps/api/.env`

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

### Generate API types

- `pnpm gen:api`

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

- If Next.js refuses to start due to Node version, run `nvm use 20` and retry.
- If `uv` is not found after installing, run `source $HOME/.local/bin/env` (and add it to your shell profile).
