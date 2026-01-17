# Provider & Data Plan (US, Free-First) — WIP

This document defines how PSMA ingests and reconciles data from multiple providers.

## 1. Goals

- Support multiple providers concurrently.
- Preserve provenance and conflicts.
- Enable expansion in Phase 2 without changing core planner.
- Keep MVP feasible with free/low-cost sources and a manual fallback.

## 2. Provider categories

- **Availability providers**: where/when a show is streamable.
- **Metadata providers**: show identity, titles, seasons/episodes.
- **Release-date research** (optional): unknown future dates.
- **Ratings providers** (future): parental guidance/suitability.

MVP can start with a minimal set and grow.

## 3. Provider contract requirements

Every provider output must include provenance:
- `provider_id`
- `retrieved_at`
- `confidence` (provider-supplied or computed)
- optional `source_ref` (URL/id)

Provider outputs must be normalized into the internal canonical schema.

## 4. Merge and conflict strategy

### Canonical view
PSMA maintains:
- raw provider facts
- a canonical merged view used for planning
- explicit conflicts where sources disagree

### Deterministic merge policy (baseline)
- Prefer more recent facts.
- Prefer higher-confidence providers.
- Prefer facts that provide explicit availability windows over vague statements.

### Conflicts as first-class
If data cannot be reconciled safely, record a conflict object rather than forcing a choice.

## 5. Manual import provider (required for MVP)

Reason:
- Ensures pilot usability even if external providers are incomplete or unavailable.

Requirements:
- Accept a simple CSV/JSON format for:
  - shows
  - services
  - availability windows
- Attach provenance as `provider_id = manual_import`.

## 6. Freshness and refresh

- Refresh is scheduled and/or user-triggered.
- Store refresh history:
  - when each provider ran
  - whether it succeeded
  - error messages

## 7. Rate limiting and resilience

- Provider calls must be rate-limit aware.
- Partial provider failure does not break the system:
  - results are merged from available providers
  - failed providers are reported

## 8. Data quality UX support

- Surface confidence indicators.
- Surface conflicts.
- Allow user override where needed (stored as user-confirmed resolution).

## 9. Provider selection checklist (before adding a provider)

- Terms of use acceptable for intended deployment.
- Coverage for US availability.
- Update frequency.
- Rate limits and API key requirements.
- Ability to store provenance references.

## 9.1 Future: Premium providers (paid tier)

Premium APIs may be added to improve accuracy and coverage (especially for live bundle/EPG and richer availability windows).

Guidelines:
- Treat premium providers as optional adapters; do not couple planner correctness to paid sources.
- Prefer providers that offer explicit availability windows and/or network airing data.
- Store provenance for premium data the same way as free sources (provider id, retrieved_at, confidence, source_ref).
- If premium data conflicts with free data, record conflicts rather than silently overriding.

Additional checklist items for premium providers:
- Commercial terms compatible with intended deployment.
- Rate limits and cost model are understood (and enforceable).
- Data retention and redistribution rules are documented.

## 10. Open questions

- Which initial free providers are acceptable from a ToS and reliability perspective?
- What is the minimum “coverage indicator” we must show to avoid misleading users?
