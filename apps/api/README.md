# PSMA API (FastAPI)

## Prereqs

- Install `uv`: https://docs.astral.sh/uv/
- Ensure a Python 3.12.x is available (uv can manage Python versions).

## Setup

From repo root:

- `cd apps/api`
- `uv sync --dev`

## Run (dev)

- `uv run uvicorn psma_api.main:app --reload --host 0.0.0.0 --port 8000`

## Logging

Logging defaults to structured JSON on stdout.

Defaults by environment (`PSMA_ENV`):

- `local` / `dev` / `development`: text logs + `DEBUG`
- anything else (e.g. `prod` / `production`): json logs + `INFO`

Environment variables:

- `PSMA_LOG_LEVEL` (default: `INFO`)
- `PSMA_LOG_FORMAT` (default: `json`, options: `json` | `text`)
- `PSMA_ENV` (default: `local`)
- `PSMA_LOG_UVICORN_ACCESS` (default: `1` in dev, `0` otherwise)

Request context:

- Every response includes `X-Request-ID`.
- If a request provides `X-Request-ID`, PSMA will reuse it.
- Logs are automatically enriched with `request_id` for in-request logs (including outbound provider HTTP logs).

See also: [docs/technical/16-Logging.md](../../docs/technical/16-Logging.md)

## Lint: policing log discipline

We avoid ad-hoc console output in app code.

- `ruff` is configured to forbid `print()` in `psma_api/*` (except CLI helpers).
- Run: `cd apps/api && uv run ruff check`

## API Docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Provider Endpoints (dev)

TVmaze (no key required):

- `GET /providers/tvmaze/search/shows?q=girls`
- `GET /providers/tvmaze/shows/{show_id}?embed=episodes`

TMDB (requires `PSMA_TMDB_API_KEY`):

- `GET /providers/tmdb/search/tv?query=Breaking+Bad`
- `GET /providers/tmdb/tv/{series_id}/watch/providers?country=US`
- List providers for a region (to populate a selector):
	- `GET /providers/tmdb/watch/providers/tv?country=US&language=en-US`
- Discover shows by selected provider (example: Netflix=8):
	- `GET /providers/tmdb/discover/tv?watch_provider_id=8&country=US&monetization_types=flatrate,free&sort_by=popularity.desc&page=1`

Notes:

- TVmaze data is licensed CC BY-SA; attribution + ShareAlike compliance is required.
- TMDB watch-provider data requires JustWatch attribution (per TMDB docs).

## Export OpenAPI

From repo root:

- `pnpm gen:openapi`

This writes the OpenAPI document to `contracts/openapi/psma.openapi.json`.
