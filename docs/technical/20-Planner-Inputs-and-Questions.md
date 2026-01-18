# Planner Inputs and Questions (Extensible, Deterministic)

This document describes how PSMA planning is **deterministic** while still being **open-ended** (extensible) in the kinds of information it can request and consume.

It covers:
- The contract shapes for `inputs[]` (request) and `questions[]` (response).
- Determinism rules (ordering, tie-breakers, “last wins”).
- The current v1 key registry (what keys exist today, expected types, and meaning).
- How to add new keys/questions without breaking clients.

## Goals

- Keep planning outputs deterministic for the same inputs.
- Allow adding new planner inputs/questions over time without needing to redesign the API every time.
- Keep UI/agents able to gather missing information in a structured way.

## Non-goals

- Defining all future personalization data in advance.
- Making the planner “magic” or non-transparent.

## Contract Summary

### Request: `PlanRequestV1`

Contract:
- JSON Schema: `contracts/jsonschema/planning/plan-request.v1.schema.json`
- API model: `apps/api/psma_api/models/planning.py` (`PlanRequestV1`)

New field:
- `inputs: PlanningInputV1[]` (optional; defaults to empty)

`PlanningInputV1` shape:
- `key: string` — stable identifier for the input (extensible)
- `value: any JSON` — JSON-compatible value (scalar, object, array)
- `service_id?: string | null` — optional scope
- `title_ids?: string[] | null` — optional scope
- `source_id?: string | null` — provenance (e.g., `ui`, `import`, `ai_suggested`)
- `collected_at?: datetime | null` — when gathered
- `notes?: string | null` — optional human notes

### Response: `PlanResponseV1`

Contract:
- JSON Schema: `contracts/jsonschema/planning/plan-response.v1.schema.json`
- API model: `apps/api/psma_api/models/planning.py` (`PlanResponseV1`)

New field:
- `questions: PlanQuestionV1[]` (optional; omitted when empty)

`PlanQuestionV1` shape:
- `id: string` — stable identifier used to de-duplicate questions
- `key: string` — stable question key (extensible)
- `prompt: string` — user-facing question
- `required: boolean`
- `service_id?: string | null` — optional scope
- `title_ids?: string[] | null` — optional scope
- `answer_schema?: object | null` — optional JSON Schema fragment describing the expected answer type
- `rationale?: string | null` — optional explanation of why it matters

## Determinism Rules

The planner must remain deterministic for a given request.

Current v1 behavior is implemented in:
- `apps/api/psma_api/engines/planner_v1.py`

Determinism principles:

1) **Stable ordering**
- Services are processed in sorted `service_id` order.
- `title_ids` and `reason_codes` are emitted as sorted unique sets.

2) **Input conflict resolution is deterministic**
- For `inputs[]`, the planner uses a simple “last wins” rule for the same `(key, service_id)`.
- This is deterministic as long as the caller controls request order.

3) **Question de-duplication is deterministic**
- Questions are keyed by `question.id`.
- If duplicates exist, the last one wins.
- Output questions are sorted by `id`.

4) **No hidden randomness**
- Planning should not depend on non-deterministic sources.
- The only time-based value is `generated_at` / `effective_at` which uses server `now`.

## Current Planner Behavior (v1)

Planner endpoint:
- `POST /plan/v1/generate`

Core rules:

- For a known/plannable service that is `availability_now == "true"` for at least one assessment:
  - Emit a `subscribe` event at `now`.

- Emit an `unsubscribe` event **only** when required inputs are present.

### Unsubscribe Scheduling (current v1)

Current required inputs (service-scoped):
- `min_contract_days` (integer > 0)
- `estimated_watch_days` (number > 0)

Computation:
- `total_days = max(min_contract_days, ceil(estimated_watch_days))`
- `unsubscribe_at = subscribe_at + total_days`
- Unsubscribe is emitted only if `unsubscribe_at` is within `horizon_days`.

If required inputs are missing:
- Planner emits `questions[]` asking for them.

## Key Registry (v1)

This is a documentation registry (not enforced by schema beyond the envelope). Add keys here as they are introduced.

### Request input keys

- `min_contract_days`
  - Scope: `service_id` required
  - Type: integer
  - Meaning: Minimum number of days the user must remain subscribed (billing/contract minimum).
  - Notes: Often 30 days for monthly services, but the goal is to be accurate per service and locale.

- `estimated_watch_days`
  - Scope: `service_id` required
  - Type: number
  - Meaning: Estimated number of days the user will take to watch what they intend to watch on this service.
  - Sources: user input, inferred watch pace, derived from episodes × runtime.

### Response question keys

- `min_contract_days`
  - Expected answer type: `{ "type": "integer", "minimum": 1 }`

- `estimated_watch_days`
  - Expected answer type: `{ "type": "number", "minimum": 0.1 }`

## Examples

### Example 1: Missing inputs (planner asks questions)

Request:
```json
{
  "country": "US",
  "horizon_days": 30,
  "permanent_service_ids": [],
  "assessments": [
    {
      "title_id": "tmdb:tv:66732",
      "country": "US",
      "service_id": "netflix",
      "provider_category": "svod",
      "availability_now": "true",
      "confidence": "high",
      "reason_codes": ["TMDB_WATCH_PROVIDER_PRESENT", "SERVICE_ID_MAPPED"],
      "evidence": [{ "source_id": "tmdb_watch_providers", "retrieved_at": "2026-01-01T00:00:00Z" }]
    }
  ]
}
```

Response (shape):
- Contains a `subscribe` event.
- Contains `questions[]` for missing inputs.

### Example 2: Inputs provided (planner emits unsubscribe)

Request (add `inputs[]`):
```json
{
  "country": "US",
  "horizon_days": 60,
  "permanent_service_ids": [],
  "inputs": [
    {"key": "min_contract_days", "service_id": "netflix", "value": 30, "source_id": "ui"},
    {"key": "estimated_watch_days", "service_id": "netflix", "value": 10, "source_id": "ui"}
  ],
  "assessments": [
    {
      "title_id": "tmdb:tv:66732",
      "country": "US",
      "service_id": "netflix",
      "provider_category": "svod",
      "availability_now": "true",
      "confidence": "high",
      "reason_codes": ["TMDB_WATCH_PROVIDER_PRESENT", "SERVICE_ID_MAPPED"],
      "evidence": [{ "source_id": "tmdb_watch_providers", "retrieved_at": "2026-01-01T00:00:00Z" }]
    }
  ]
}
```

Expected result:
- `events[]` contains both `subscribe` and `unsubscribe` for `netflix`.
- `questions` is absent (or empty).

## How to Add New Inputs / Questions

Additive changes should be easy and safe.

1) **Choose a stable `key`**
- Prefer descriptive, snake_case keys (e.g., `watch_hours_per_week`, `episodes_per_day`).
- Avoid service-specific keys unless truly service-specific.

2) **Document the key here**
- Add scope, expected type, and meaning.

3) **Update planner behavior deterministically**
- Parse the new key from `request.inputs`.
- Decide how it affects event timing.
- Ensure ordering/tie-break rules remain stable.

4) **Emit a `question` when missing**
- Add a `PlanQuestionV1` with stable `id`.
- Include `answer_schema` when possible.

5) **Update tests**
- Add/adjust tests in `apps/api/tests/test_planning_v1.py`.

6) **Update UI rendering (optional)**
- The smoke UI currently renders questions as a simple list.
- Product UI can later implement richer “answer capture” flows without changing the API shape.

## Notes on Python/Environment

The API project specifies Python 3.12 in `apps/api/pyproject.toml` (`requires-python = ">=3.12,<3.13"`).

If your local environment uses a different Python version, ensure dependencies are installed from `apps/api/pyproject.toml`.
