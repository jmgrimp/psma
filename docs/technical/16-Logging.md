# Logging

This document describes PSMA’s logging foundation and the conventions new developers should follow.

Goals:

- Consistent, structured logs suitable for production aggregation
- Human-friendly logs in local development
- Request correlation across inbound API calls and outbound provider calls
- Minimal dependencies (stdlib `logging`)

Non-goals:

- Full tracing/metrics/OTel (can be layered on later)

## Where logging is configured

- API logging setup: [apps/api/psma_api/logging_config.py](../../apps/api/psma_api/logging_config.py)
- Request context storage: [apps/api/psma_api/logging_context.py](../../apps/api/psma_api/logging_context.py)
- Request logging middleware: [apps/api/psma_api/main.py](../../apps/api/psma_api/main.py)
- Outbound HTTP logging hooks: [apps/api/psma_api/deps.py](../../apps/api/psma_api/deps.py)

## Environments and defaults

Logging behavior defaults based on `PSMA_ENV` unless explicitly overridden:

- `local` / `dev` / `development`
  - `PSMA_LOG_FORMAT=text`
  - `PSMA_LOG_LEVEL=DEBUG`
  - uvicorn access logs enabled by default
- anything else (e.g. `prod` / `production`)
  - `PSMA_LOG_FORMAT=json`
  - `PSMA_LOG_LEVEL=INFO`
  - uvicorn access logs disabled by default (to reduce noise)

Overrides:

- `PSMA_LOG_LEVEL` — force a level (e.g. `DEBUG`, `INFO`, `WARNING`)
- `PSMA_LOG_FORMAT` — `json` | `text`
- `PSMA_LOG_UVICORN_ACCESS` — `1`/`0` to enable/disable uvicorn access logs

## Log schema (JSON)

When `PSMA_LOG_FORMAT=json`, each log line is a JSON object with these stable top-level keys:

- `ts` — ISO timestamp (UTC)
- `level` — `DEBUG` | `INFO` | `WARNING` | `ERROR`
- `logger` — logger name (e.g. `psma_api`, `psma_api.http`)
- `message` — human-readable message / event name
- `service` — defaults to `psma-api` (override via `PSMA_SERVICE`)
- `env` — defaults to `local` (from `PSMA_ENV`)
- `version` — defaults to `0.0.0` (override via `PSMA_VERSION`)

Optional structured fields (present when relevant):

- `request_id` — request correlation id
- `method`, `path` — HTTP method/path
- `status_code` — HTTP status
- `duration_ms` — latency in milliseconds
- `upstream` — upstream host (e.g. `api.themoviedb.org`)
- `url` — sanitized URL (query stripped)
- `exc_info` — exception traceback (only on exception logs)

## Request correlation (X-Request-ID)

PSMA assigns a request id for every inbound request:

- If the client sends `X-Request-ID`, PSMA will reuse it.
- Otherwise PSMA generates a UUID.
- The response always includes `X-Request-ID`.

All logs written during a request automatically include `request_id` using a `contextvars`-based filter.

## Request logging policy

The request middleware logs a single `request_completed` event for every request with method/path/status/latency.

Severity is based on status code:

- `< 400` → `INFO`
- `400–499` → `WARNING`
- `>= 500` → `ERROR`

Exceptions raised while handling the request are logged as `request_failed` with stack trace.

## Outbound HTTP logging policy

Outbound provider calls are logged via `httpx` event hooks:

- `upstream_request` (DEBUG)
- `upstream_response` (DEBUG)

Notes:

- URLs are sanitized to avoid leaking secrets in query parameters (TMDB `api_key`).
- These logs inherit `request_id` automatically when the outbound call happens during an inbound request.

## How to log in code (conventions)

Use stdlib `logging` and structured `extra` fields.

Example:

```python
import logging

logger = logging.getLogger("psma_api.providers")

logger.info(
    "provider_refresh_started",
    extra={"provider": "tmdb", "country": "US"},
)
```

Conventions:

- Use event-like messages (snake_case) rather than long prose.
- Prefer stable field names (`provider`, `country`, `show_id`, etc.).
- Never log secrets (API keys, tokens, session cookies, full query strings).

## Policing: preventing ad-hoc output

We discourage logging outside the configured system.

- Python: `ruff` forbids `print()` usage inside `psma_api/*` (except CLI helpers).
  - Run: `cd apps/api && uv run ruff check`

## Troubleshooting

- Need more detail locally?
  - Set `PSMA_LOG_LEVEL=DEBUG` and `PSMA_LOG_FORMAT=text` in `apps/api/.env`
- Need to see upstream HTTP calls?
  - Upstream logs are `DEBUG`, so ensure level includes DEBUG.
- Seeing too much noise in production?
  - Keep `PSMA_ENV=prod` and do not set `PSMA_LOG_LEVEL=DEBUG` unless debugging.
