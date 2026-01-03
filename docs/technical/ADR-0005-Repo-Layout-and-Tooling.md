# ADR-0005: Repo Layout and Tooling (Monorepo)

- **Status:** Accepted
- **Date:** 2026-01-02

## Context

PSMA needs:
- a Next.js web UI
- a Python/FastAPI backend API
- contract-first boundaries (OpenAPI)
- low-friction local development for a small team

We want a setup that remains maintainable as PSMA grows, without introducing unnecessary tooling early.

## Decision

### 1) Use a simple monorepo without a heavyweight monorepo manager
- Use **pnpm workspaces** (root `pnpm-workspace.yaml`) to manage Node packages.
- Do **not** introduce Nx/Lerna initially.

### 2) Repo layout
- `apps/web`: Next.js UI (runs on `:3000`)
- `apps/api`: FastAPI backend (runs on `:8000`)
- `packages/api-client`: OpenAPI-derived TypeScript types for clients
- `contracts/`: versionable API contracts

### 3) API typing strategy
- Generate an OpenAPI document from the FastAPI app into `contracts/openapi/psma.openapi.json`.
- Generate TypeScript types from that OpenAPI document into `packages/api-client`.

### 4) Tooling choices
- **Backend dependency management:** `uv`
- **Frontend package manager:** `pnpm`
- **Node version:** >= 20.9 (tracked via `.nvmrc` / `.node-version`)

## Rationale

- pnpm workspaces provide enough structure for 2 apps + a small shared TS package.
- Avoiding Nx/Lerna reduces setup overhead and cross-language complexity.
- Contract-first type generation prevents UI/backend drift.

## Consequences

- Developers run API and UI in separate processes.
- We add a monorepo manager later only if:
  - the number of apps/packages grows substantially, or
  - CI build times and dependency graphs require caching/affected builds.

## Related

- [docs/technical/ADR-0001-Backend-Stack-and-MultiTenancy.md](ADR-0001-Backend-Stack-and-MultiTenancy.md)
- [docs/technical/14-API-and-Contract-Outline.md](14-API-and-Contract-Outline.md)
