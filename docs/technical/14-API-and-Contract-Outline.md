# API and Contract Outline — WIP

This document outlines external API capabilities and internal contract artifacts needed for backlog confidence.

## 1. Contract-first artifacts (planned)

- **External API**: OpenAPI spec
- **Provider outputs**: JSON Schema
- **AI outputs**: JSON Schema

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
- `POST /plan/generate`
- `GET /plan`
- `GET /plan/delta` (latest delta vs prior)

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

- External API versioned under `/v1`.
- Provider/AI schemas carry `contract_version`.

## 4. Open questions

- Which endpoints are required for MVP UI vs future mobile?
- Should the UI consume plan delta separately or as part of a plan response?
