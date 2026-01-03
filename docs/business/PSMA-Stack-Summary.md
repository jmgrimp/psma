# PSMA Stack Summary (Non-Technical)

## Purpose

This document summarizes the technology choices for PSMA in plain language: what we’re building on, why, and what we’re intentionally deferring.

## What we’re building (in one sentence)

PSMA is a local-first app that aggregates “where/when to watch” information, lets users pick shows and viewing preferences, and produces a simple subscribe/unsubscribe plan—plus reminders—without automating purchases or cancellations.

## Stack decision (what we picked)

### Web UI

- **Framework:** Next.js
- **Package manager:** pnpm (workspace-based monorepo)
- **API typing:** TypeScript types generated from the backend OpenAPI contract

Why this fits PSMA:
- Keeps UI and backend loosely coupled via a stable API boundary.
- Makes integration safer (types reflect the contract).
- Supports future UIs (mobile/CLI) without rewriting core logic.

### Backend API
- **Language/runtime:** Python
- **Web framework:** FastAPI

Why this fits PSMA:
- **Stable, mature ecosystem** for APIs and data modeling.
- **Good fit for AI-adjacent workflows** (even if we later add more than basic LLM calls).
- **Separates cleanly** into an API and a background worker process as the app grows.

### Data storage
- **MVP (standalone/local-first):** SQLite (single-file database)
- **Future hosted (multi-user):** Postgres
- **Multi-tenant approach when hosted:** single shared database/schema with a required `tenant_id` field on tenant-scoped data

Why this fits PSMA:
- SQLite keeps the MVP low-cost and easy to run.
- Postgres is the standard upgrade path for hosted and multi-user operation.
- The `tenant_id` approach keeps hosted operations simpler than running one database per tenant.

### Background work (refresh + AI)
PSMA will run background tasks in a **separate worker process** (still in the same repo at first) for:
- refreshing provider data
- detecting changes/conflicts
- generating advisory AI guidance

Why this fits PSMA:
- Keeps the API responsive.
- Isolates “spiky” workloads (provider calls, LLM calls).

### AI integration (vendor-flexible)
PSMA integrates AI behind a plug-in style adapter, and supports **OpenAI-compatible APIs**, including **OpenRouter**, via configuration:
- base URL
- model
- API key

AI is **advisory and confirmation-based**:
- it suggests and asks questions
- users confirm changes
- AI does not silently edit preferences or invent catalog facts

## What we intentionally did NOT decide yet

These are choices we can defer until implementation without risking rework, because the architecture is modular:
- **UI technology** beyond “simple web UI first” (the API boundary stays stable)
- **Reminder channel** details (in-app vs calendar export vs email)
- **Which providers we use first** (depends on ToS, coverage, and feasibility)
- **Which hosting platform** (only needed once we move beyond standalone)

We are also intentionally deferring Docker/containerization for MVP. It can be added later for reproducible builds and hosted deployments.

## Risks and mitigations

- **Provider coverage and licensing/ToS:** “where to watch” data can be the hardest part.
  - Mitigation: best-effort + provenance + manual import fallback.
- **SQLite → Postgres migration later:** differences in concurrency and SQL behavior.
  - Mitigation: keep schema/migrations disciplined; treat MVP as “future-aware.”
- **Multi-tenant safety when hosted:** `tenant_id` must be enforced consistently.
  - Mitigation: enforce at a single boundary and add tests.

## Source of truth

This summary is derived from the technical decision record:
- [docs/technical/ADR-0001-Backend-Stack-and-MultiTenancy.md](../technical/ADR-0001-Backend-Stack-and-MultiTenancy.md)
