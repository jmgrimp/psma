## PSMA Copilot Instructions

This repository is the **Program Subscription Manager Application (PSMA)**.

PSMA is designed to:
- Aggregate show availability from **multiple providers** (best-effort, US-first).
- Let users select shows + preferences.
- Generate a deterministic subscribe/unsubscribe plan.
- Use AI/agents to provide guidance and ask questions when data changes.

### Guiding principles

1) **Docs-first when planning**
- When a request is architectural/product planning, prioritize updating docs under `docs/` and `docs/technical/`.
- Keep marketing language out of technical docs.

2) **Contract-first and modular by default**
- Treat the system as core + ports/adapters.
- Define and maintain stable contracts for:
  - external API (OpenAPI)
  - provider outputs (JSON schema)
  - engine outputs (JSON schema; e.g., availability assessments)
  - AI outputs (JSON schema)
- Avoid coupling UI logic to planning logic; UI must call a stable API boundary.

Contract locations (current convention):
- OpenAPI: `contracts/openapi/`
- JSON Schemas: `contracts/jsonschema/`
- Curated registries (e.g., service identity mapping): `contracts/registry/`

3) **Backend stack decision (current direction)**
- Primary backend: **Python + FastAPI**.
- MVP storage: **SQLite**.
- Hosted/multi-tenant target: **Postgres** with a **single shared schema** and mandatory `tenant_id`.
- Background work (provider refresh, diffing, AI) runs in a separate worker process (same repo initially).

4) **AI behavior**
- AI is **advisory** and **confirmation-based**:
  - Suggest changes and await user confirmation.
  - Do not silently change user preferences or facts.
- Support role-based “agent bios” (e.g., scheduler vs researcher) via configuration.
- LLM provider must be configurable for developer experimentation, including **OpenRouter** (OpenAI-compatible API).
- Keep provenance and confidence visible for any data-driven claim.

5) **Multi-provider data strategy**
- Always store provenance for imported facts (provider id, retrieved timestamp, confidence, optional source reference).
- Conflicts are first-class: record them rather than hiding disagreements.

### Development rules

- Prefer small, incremental changes.
- Avoid introducing new frameworks unless explicitly requested.
- Avoid hard-coding vendor-specific behavior; use configuration and adapters.
- Add tests for deterministic planning and contract validation when introducing new contracts.

### Tooling and execution

- Do not install VS Code extensions unless explicitly requested.
- Do not run expensive commands unless asked.
- When running Python, use the workspace’s configured Python environment tooling.
