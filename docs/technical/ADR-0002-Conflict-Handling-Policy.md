# ADR-0002: Conflict Handling Policy (MVP)

- **Status:** Accepted
- **Date:** 2025-12-31

## Context

PSMA ingests catalog and availability facts from multiple providers. Providers may disagree (conflicts) about:
- whether two show identities are the same
- which service currently has availability for a show
- start/end dates of availability windows

Conflicts are expected and must be handled without silently misleading users.

MVP requirements:
- best-effort data
- provenance visible
- confirmation-based UX for changes

## Decision

### 1) Conflicts are first-class objects
When providers disagree beyond a safe threshold, PSMA records a conflict object and preserves competing facts and provenance.

### 2) MVP default planning policy: "plan with warnings" (non-blocking)
MVP will **not block** plan generation for most conflicts.

Instead, it will:
- choose a deterministic “working assumption” for planning
- label affected plan events as **contested**
- present a conflict-resolution prompt to the user

### 3) Blocking conflicts (rare)
MVP will block planning for a specific show only when:
- no service can be selected deterministically (e.g., all candidate services have confidence below a minimum threshold), OR
- the show identity match is unresolved and impacts selection integrity (e.g., two different shows may be merged incorrectly)

In these cases, the system produces:
- a partial plan for unaffected shows
- a clear user question to resolve the blocked item

### 4) Confirmation-based resolution
- User-selected conflict resolutions are stored as user-confirmed overrides with provenance: `source = user_confirmation`.
- Future refreshes may raise new conflicts if underlying facts change.

## Rationale

- Non-blocking planning supports internal pilot usability.
- Deterministic working assumptions keep planner testable.
- Contested labeling prevents false certainty.

## Consequences

- UI must support:
  - viewing conflicts
  - showing “contested” plan items
  - confirming a resolution
- Planner must accept a canonical view plus a list of contested facts and propagate them into plan rationale.

## Related

- [docs/technical/12-Provider-Data-Plan.md](12-Provider-Data-Plan.md)
- [docs/technical/15-Golden-Scenarios.md](15-Golden-Scenarios.md)
