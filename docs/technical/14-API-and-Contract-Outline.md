# API and Contract Outline — WIP

This document outlines the external API capabilities and the contract artifacts used to keep UI, adapters, and engines aligned.

## 1. Contract-first artifacts (current + planned)

### External API (current)

- **OpenAPI**: `contracts/openapi/psma.openapi.json`
- Generate/update it via `pnpm gen:openapi`

### Internal contracts (current)

- **Availability engine outputs** (JSON Schema):
	- `contracts/jsonschema/availability/availability-assessment.v1.schema.json`
	- `contracts/jsonschema/availability/availability-assessments-response.v1.schema.json`
- **Planner outputs** (JSON Schema):
	- `contracts/jsonschema/planning/plan-request.v1.schema.json`
	- `contracts/jsonschema/planning/plan-response.v1.schema.json`
- **Curated registries** (data normalization, checked-in):
	- `contracts/registry/service-registry.v1.json` (canonical `service_id` mappings)

### Internal contracts (planned)

- **Provider raw fact outputs** (JSON Schema) for each adapter (e.g., TMDB watch-provider snapshots).
- **AI outputs** (JSON Schema) for advice/questions and user confirmations.

## 2. External API capabilities (conceptual)

### Catalog
- `GET /shows?status=...&region=US`
- `GET /shows/{show_id}`
- `GET /availability?show_id=...&region=US`
- `POST /catalog/refresh`

### Selections
- `GET /my-shows`
- `POST /my-shows` (upsert preference)
- `DELETE /my-shows/{show_id}`

### Planning
- Implemented (stable façade):
	- `POST /plan/v1/generate`
- Planned:
	- `GET /plan`
	- `GET /plan/delta` (latest delta vs prior)

Notes:
- Planning v1 supports an extensible `inputs[]` request field and optional `questions[]` response field for gathering missing personalization data in a structured way.
- See `docs/technical/20-Planner-Inputs-and-Questions.md`.

### Conflicts
- `GET /conflicts`
- `POST /conflicts/{conflict_id}/resolve`

### AI suggestions/questions
- `GET /advice` (pending recommendations/questions)
- `POST /advice/{id}/confirm`
- `POST /advice/{id}/decline`

### Reminders
- `GET /reminders/ics` (calendar export)

## 3. Versioning

- OpenAPI is treated as versionable output under `contracts/openapi/`.
- JSON Schemas are versioned by filename (e.g., `*.v1.schema.json`).
- Whether the REST API uses a `/v1` prefix is a future decision; the OpenAPI document is the source of truth.

## 4. Open questions

- Which endpoints are required for MVP UI vs future mobile?
- Should the UI consume plan delta separately or as part of a plan response?
