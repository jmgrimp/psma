# ADR-0001: Backend Stack and Multi-Tenancy Approach

- **Status:** Accepted
- **Date:** 2025-12-31

## Context

PSMA is intended to:
- Run as a low-cost, local-first MVP for internal trial users.
- Evolve into a hosted, multi-tenant service.
- Support multiple UIs (web now; mobile later) through stable API contracts.
- Incorporate multiple data providers (catalog/availability) via a plugin architecture.
- Provide AI/agent-driven guidance that is confirmation-based, with pluggable LLM providers (OpenRouter).

Key constraints and preferences:
- Team comfort is not a deciding factor.
- Preference to avoid excessive ecosystem churn (“ephemeral JS” concern).
- Future split into separate services/processes is acceptable.
- Multi-tenancy target: **single shared Postgres schema**.

## Decision

### Backend runtime and framework
- **Primary backend language/runtime:** Python
- **API framework:** FastAPI

### Data storage
- **MVP/local-first:** SQLite
- **Hosted/multi-tenant:** Postgres
- **Multi-tenancy model:** Single shared database/schema with mandatory `tenant_id` on tenant-scoped records.

### Background processing
- Use a separate **worker process** (can be the same codebase) to perform:
  - provider refresh/ingestion
  - diff/change detection
  - conflict detection
  - AI guidance generation

The architecture must allow the worker to be split into an independent service later if needed.

### Contract-first boundaries
- **External API:** OpenAPI (generated from the API layer)
- **Internal contracts:** JSON Schema for:
  - provider outputs (normalized facts + provenance)
  - AI outputs (recommendations/questions/explanations + confidence + sources)

### LLM integration
- LLM access is behind a port/adapter with runtime configuration supporting OpenRouter:
  - configurable base URL
  - configurable model
  - configurable API key

AI outputs are advisory and confirmation-based.

## Rationale

- **Stability preference:** Python backend ecosystem (FastAPI + SQLAlchemy/Alembic) is relatively stable and mature.
- **AI-readiness:** Python is well-suited if PSMA later adds heavier AI/ML functionality beyond LLM API calls.
- **Scalability:** Stateless API + worker separation scales horizontally and isolates ingestion/LLM workloads.
- **Multi-tenancy:** Single shared Postgres schema is a common, operationally simpler approach for early multi-tenant products.
- **Modularity:** Contract-first boundaries preserve a plugin/adapter architecture and reduce coupling to frameworks.

## Consequences

### Positive
- Clear path from standalone MVP → hosted multi-tenant.
- Worker separation reduces coupling and simplifies scaling provider refresh operations.
- Vendor/model experimentation for LLMs is easy via adapters (OpenRouter-compatible).
- Multi-UI support is enabled by stable, versionable API contracts.

### Trade-offs / Risks
- SQLite → Postgres migration must be planned (migrations, dialect differences, concurrency).
- Multi-tenant shared schema requires strict enforcement of `tenant_id` in queries (middleware + tests).
- Python plugin systems are typically validated at runtime; mitigate with JSON Schema validation + contract tests.

## Implementation notes (non-binding)

- Enforce `tenant_id` scoping at a single boundary (e.g., request context/middleware) and ensure every repository/query requires it.
- Treat “single-user MVP” as a default tenant/user internally rather than special-casing.
- Use job records (DB-backed) for MVP scheduling/queueing; evolve to a dedicated queue if needed.
- Store provenance on imported facts:
  - provider id
  - retrieved timestamp
  - confidence score
  - optional source reference

## Related documents

- [docs/technical/00-Architecture-Overview.md](00-Architecture-Overview.md)
- [docs/technical/02-Ports-and-Adapters.md](02-Ports-and-Adapters.md)
- [docs/technical/03-AI-Agent-System.md](03-AI-Agent-System.md)
- [docs/technical/04-Data-Flow-and-Events.md](04-Data-Flow-and-Events.md)
- [docs/technical/05-Security-and-Identity.md](05-Security-and-Identity.md)
