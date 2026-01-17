# MVP PRD (Tech-Only) — WIP

This document defines MVP scope and assumptions in a way that supports backlog creation.

## 1. Product intent (MVP)

PSMA MVP enables a US-based internal pilot user to:
- browse a best-effort catalog of shows and availability
- select shows and set per-show viewing preferences
- generate a deterministic subscribe/unsubscribe instruction plan
- receive guidance and questions (AI advisory, confirmation-based)

## 2. MVP scope (in)

### Catalog
- US region scope.
- Multiple provider ingestion (at least 1 provider + manual import provider).
- Provenance stored on every imported fact.
- Canonical merged view + conflicts recorded.

### Selections & preferences
- Add/remove shows.
- Set per-show watch mode:
  - `as_aired`
  - `binge_after_season`
- If binge mode: set a binge duration (days).
- Maintain a user service profile:
  - mark services as “permanent” (always-on) so the planner does not recommend subscribing/unsubscribing those services

### Planning
- Deterministic plan generation given the same inputs.
- Planning is engine-driven:
  - Availability Engine(s) produce canonical availability assessments from heterogeneous provider facts.
  - Planner consumes those assessments + user preferences/service profile and generates the subscription plan.
- Plan output includes:
  - dated `subscribe`/`unsubscribe` events per service
  - a rationale for each event (what drove it)
  - explicit assumptions when data is incomplete (e.g., unknown end dates)

### AI guidance (minimal, high-value)
- AI provides:
  - recommendations (e.g., “binge is cheaper for this service behavior”)
  - targeted questions when ambiguity blocks planning
- AI is confirmation-based:
  - no silent preference changes
  - no silent “fact changes” to catalog

### Reminders
- Provide reminders without automation:
  - in-app upcoming events list and/or calendar export (ICS)

## 3. MVP out of scope (explicit)

- Automated subscribe/unsubscribe execution.
- Guaranteed full catalog coverage across all services.
- Full pricing/billing-cycle optimization (time-minimization first).
- Multi-tenant hosted operation (MVP runs single-user mode, but data model is future-aware).
- Safety/age-suitability answers (requires ratings provider and policy).
- Premium data-provider integrations and paid-tier features (future).

## 4. Assumptions (must be explicit)

### Availability assumptions
- Availability is represented as windows: `available_from` and optional `available_until`.
- If `available_until` is unknown:
  - planner uses a conservative default horizon and flags the assumption in rationale.
- Some services are treated as “permanent” by the user (e.g., YouTube TV as a cord-cutting bundle):
  - planner must treat them as already-subscribed for the plan horizon
  - planner may still recommend *non-permanent* add-on subscriptions alongside them

### Optimization target (MVP)
- Primary objective: minimize *time subscribed* while meeting user watch-mode constraints.
- If multiple services offer the same show, MVP behavior must be defined:
  - default to a deterministic tie-breaker (e.g., highest-confidence availability)
  - record that alternatives exist

### Release pattern knowledge (SBKB)
- Release pattern facts are curated (v1) and treated as advisory signals.

## 5. MVP workflows (user-visible)

### W1: Select and plan
1) User refreshes catalog (or catalog is already refreshed).
2) User browses shows.
3) User adds show to “My Shows” and selects watch mode.
4) User generates plan.
5) User reviews plan events.

### W2: Data changes and confirmation
1) Provider refresh happens.
2) System detects changes/conflicts that impact user.
3) System computes plan delta.
4) AI produces explanation + recommendations/questions.
5) User confirms changes.
6) System regenerates plan and updates reminders.

## 6. MVP acceptance criteria (system-level)

- A user can produce a plan from selected shows and view it.
- The plan is deterministic.
- The system records provenance for imported facts.
- Conflicts are visible and resolvable via confirmation.
- AI never silently changes preferences or catalog facts.

Engine contract constraints:
- Engine outputs are validated against versioned JSON Schemas under `contracts/jsonschema/`.
- Canonical `service_id` mappings come from curated registries under `contracts/registry/`.

## 7. MVP non-functional requirements

- Local-first operation is supported.
- Provider refresh is rate-limit aware and failure-tolerant (partial provider failures do not crash the app).
- All user data is logically user-scoped from day 1.

## 8. Open questions (to resolve before implementation backlog)

- What is the minimum set of streaming services to include in SBKB v1?
- (Resolved) Default planning horizon when `available_until` is unknown: see ADR-0003.
- (Resolved) Deterministic policy for selecting among multiple services: see ADR-0004.
- Which reminder mechanism is MVP: in-app only, ICS only, or both?

## 9. Future: Premium data sources (paid tier)

PSMA can improve availability accuracy by adding premium APIs in a paid version.

Requirements:
- Premium providers must remain optional adapters behind stable contracts.
- Outputs must include provenance and retrieval time, and must merge cleanly with free/manual sources.
- The system must remain usable without premium providers (graceful degradation).
