# ADR-0003: Unknown Availability End Date Policy (MVP)

- **Status:** Accepted
- **Date:** 2025-12-31

## Context

Many providers cannot reliably supply an `available_until` date for a show on a service.

If PSMA treats unknown end dates as “subscribe forever,” the plan becomes unrealistic and unhelpful.
If PSMA invents an end date silently, it may mislead users.

## Decision

### 1) Represent unknown explicitly
An availability window may have `available_until = unknown`.

### 2) MVP planning uses a default horizon + explicit assumption
For windows with unknown end dates, the planner will:
- compute a conservative unsubscribe date using a **default planning horizon**
- clearly label the assumption in the plan event rationale

**Default horizon values (MVP):**
- If watch mode = `binge_after_season`: unsubscribe = subscribe date + `binge_days`
- If watch mode = `as_aired`: unsubscribe = subscribe date + **30 days** (configurable)

### 3) Trigger a question when it materially affects cost/overlap
If the unknown end date causes either:
- a long continuous subscription, OR
- increased overlap with other services

then PSMA should prompt the user:
- “How long do you expect to stay subscribed to Service X for Show Y?”

User answers become explicit preferences (confirmed facts).

## Rationale

- A default horizon produces an actionable plan without pretending certainty.
- The prompt is only asked when it changes decisions materially.

## Consequences

- Planner must include assumption metadata in plan events.
- Configuration must expose default horizons.
- AI/Scheduler can reframe the question based on user history.

## Related

- [docs/technical/11-MVP-PRD.md](11-MVP-PRD.md)
- [docs/technical/13-AI-Policies-and-Workflows.md](13-AI-Policies-and-Workflows.md)
- [docs/technical/15-Golden-Scenarios.md](15-Golden-Scenarios.md)
