# ADR-0006: MVP Run Strategy (Local-First, No Docker Required)

- **Status:** Accepted
- **Date:** 2026-01-02

## Context

PSMA MVP goals include:
- minimal cost and operational overhead
- fast local iteration on a single developer machine
- a clear path to hosted deployment later

The repo contains:
- `apps/api` (FastAPI backend)
- `apps/web` (Next.js frontend)

We can run these either:
- directly on the host (two processes), or
- via Docker/Compose

## Decision

For MVP development, PSMA will be run **directly on the host**:
- Next.js dev server on `http://localhost:3000`
- FastAPI dev server on `http://localhost:8000`

Docker is **not required** for MVP and will be treated as an optional enhancement later.

## Rationale

- Lowest friction for a small team and early iteration.
- Avoids container build/debug overhead.
- Keeps the MVP aligned with “standalone/local-first” goals.

## Consequences

- Local prerequisites must be documented (Node >= 20.9, pnpm via Corepack, `uv`).
- When we introduce Docker later, it must remain optional and match the same ports.

## Related

- [docs/technical/ADR-0005-Repo-Layout-and-Tooling.md](ADR-0005-Repo-Layout-and-Tooling.md)
- [README.md](../../README.md)
