# PSMA Technical Documentation

This directory contains technical (non-marketing) documentation for the PSMA architecture.

## Contents

- [00-Architecture-Overview.md](00-Architecture-Overview.md) — high-level system view and major responsibilities
- [01-Domain-Model.md](01-Domain-Model.md) — core domain concepts and conceptual data model
- [02-Ports-and-Adapters.md](02-Ports-and-Adapters.md) — provider/LLM/reminder/UI boundaries (tech-agnostic)
- [03-AI-Agent-System.md](03-AI-Agent-System.md) — agent roles (“bios”), guardrails, and workflows
- [04-Data-Flow-and-Events.md](04-Data-Flow-and-Events.md) — refresh/diff/event model and plan lifecycle
- [05-Security-and-Identity.md](05-Security-and-Identity.md) — future-aware auth, user scoping, and auditability
- [ADR-0001-Backend-Stack-and-MultiTenancy.md](ADR-0001-Backend-Stack-and-MultiTenancy.md) — decision record for Python/FastAPI + SQLite→Postgres + shared-schema multi-tenancy
- [ADR-0002-Conflict-Handling-Policy.md](ADR-0002-Conflict-Handling-Policy.md) — conflict objects, non-blocking planning, and confirmation workflow (MVP)
- [ADR-0003-Unknown-Availability-End-Date-Policy.md](ADR-0003-Unknown-Availability-End-Date-Policy.md) — default horizons + when to ask the user (MVP)
- [ADR-0004-Deterministic-TieBreakers-and-Buffers.md](ADR-0004-Deterministic-TieBreakers-and-Buffers.md) — tie-breakers, unsubscribe buffers, and merge adjacency rules (MVP)
- [ADR-0005-Repo-Layout-and-Tooling.md](ADR-0005-Repo-Layout-and-Tooling.md) — pnpm workspaces + Next.js UI + uv backend + OpenAPI typegen
- [ADR-0006-MVP-Run-Strategy-Local-First.md](ADR-0006-MVP-Run-Strategy-Local-First.md) — run web+api locally; Docker optional later
- [10-User-Stories.md](10-User-Stories.md) — MVP and future user stories with acceptance criteria
- [11-MVP-PRD.md](11-MVP-PRD.md) — MVP scope, assumptions, and system-level acceptance criteria (WIP)
- [12-Provider-Data-Plan.md](12-Provider-Data-Plan.md) — multi-provider ingestion, merge/conflict strategy, and refresh policies (WIP)
- [13-AI-Policies-and-Workflows.md](13-AI-Policies-and-Workflows.md) — AI guardrails, roles/bios, triggers, and confirmation workflow (WIP)
- [14-API-and-Contract-Outline.md](14-API-and-Contract-Outline.md) — API surface and contract artifacts needed for backlog confidence (WIP)
- [15-Golden-Scenarios.md](15-Golden-Scenarios.md) — canonical scenarios for validation and demos (WIP)
- [16-Logging.md](16-Logging.md) — logging foundations, conventions, and environment defaults

## Diagram conventions

Diagrams are provided in Mermaid format for easy rendering in GitHub/VS Code.
