# ADR-0004: Deterministic Tie-Breakers and Buffer Policies (MVP)

- **Status:** Accepted
- **Date:** 2025-12-31

## Context

In MVP, PSMA optimizes primarily for minimizing time subscribed while meeting viewing constraints.

However, real-world inputs create ambiguity:
- the same show may be available on multiple services
- provider facts may differ in confidence and freshness
- unsubscribe timing needs a small buffer to avoid off-by-one availability assumptions

To keep the planner deterministic and testable, tie-breakers and buffers must be explicit.

## Decision

### 1) Tie-breaker when a show is available on multiple services
When multiple services offer availability for the same show in the region/time window:

1. Prefer the service/fact with the **highest confidence**.
2. If tied, prefer the fact with the **most recent retrieved_at**.
3. If still tied, prefer the service with the **lowest subscription price** *when price is known and comparable*.
4. If still tied (or price is unknown/unavailable), prefer the service with the **lowest stable sort key** (e.g., service_id lexical order).
5. If the remaining options are still meaningfully different for the user (e.g., different “permanent service” status, different ad tiers, or user preference), PSMA may ask the user to break the tie.

The planner must record that alternatives existed and that a deterministic tie-breaker was applied.

User tie-break policy:
- The planner must remain deterministic *given the same inputs*. Asking the user is allowed if the user’s choice is stored as an explicit, provenance-backed resolution (a user-confirmed fact/preference).
- Until the user responds, PSMA should either:
	- generate a **provisional** plan using the stable sort key and clearly mark it as requiring confirmation, or
	- block plan finalization for that specific decision and surface a targeted question.

Notes on price tie-breaker:
- Price inputs must be treated as time-bound facts with provenance and `retrieved_at` (prices change).
- If prices are from different tiers (ad vs ad-free) or billing cycles (monthly vs annual), PSMA must either normalize explicitly or treat them as non-comparable.
- If price is missing or non-comparable, do not block planning; fall back to the stable sort key.

### 2) Unsubscribe buffer policy
To reduce edge-case risk (time zones, “available until” semantics, provider lag):

- If `available_until` is known, unsubscribe date = `available_until` + **1 day** (configurable).

### 3) Merge policy
Per service, required subscription intervals are merged when:
- windows overlap or are adjacent within **1 day** (configurable).

### 4) Configuration
The following must be configurable (with MVP defaults above):
- unsubscribe buffer days
- merge adjacency days
- confidence threshold that triggers “contested” labeling

## Rationale

- Deterministic behavior simplifies testing and user trust.
- Buffers reduce false negatives where a user cancels too early.

## Consequences

- Canonical view must provide confidence + retrieved_at for availability facts.
- Plan rationale must include tie-breaker notes when applied.

## Related

- [docs/technical/12-Provider-Data-Plan.md](12-Provider-Data-Plan.md)
- [docs/technical/15-Golden-Scenarios.md](15-Golden-Scenarios.md)
