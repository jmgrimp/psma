# Golden Scenarios (for Validation and Backlog Confidence) — WIP

These scenarios define expected behavior and will later become test fixtures and demo flows.

## Scenario 1: Basic plan with one show, one service

- Show A available on Service X from Jan 1 to Feb 1.
- User selects Show A, watch mode = as_aired.

Expected:
- Plan subscribes to X on Jan 1.
- Plan unsubscribes from X shortly after Feb 1 (buffer policy).
- Rationale references Show A.

## Scenario 2: Two shows on same service with overlapping windows

- Show A on Service X: Jan 1–Feb 1
- Show B on Service X: Jan 15–Mar 1

Expected:
- Plan merges into a single subscription interval.

## Scenario 3: Unknown availability end date

- Show A on Service X: available_from = Jan 1, available_until = unknown.

Expected:
- Plan includes explicit assumption (default horizon or user prompt).
- System may ask user whether to keep subscription continuous or set a stop date.

## Scenario 4: Provider conflict

- Provider 1: Show A on Service X
- Provider 2: Show A on Service Y

Expected:
- Conflict recorded.
- User is asked to confirm.
- Planning either:
  - blocks plan for Show A until resolution, OR
  - uses deterministic tie-breaker and flags as contested (must be chosen).

## Scenario 5: SBKB advice (all-at-once release pattern)

- Service X release_pattern = all_at_once.
- User selects “watch as aired” for a show on Service X.

Expected:
- Scheduler agent recommends switching to binge.
- User must confirm change.

## Scenario 6: Refresh-driven plan delta

- Prior plan exists.
- Refresh moves availability earlier/later.

Expected:
- System produces a plan delta.
- AI explains the change.
- User confirms/declines.

## Scenario 7: Multi-tenant future check

- Same show exists across tenants.

Expected:
- Tenant-scoped user preferences and plans are isolated by tenant_id.

## Open questions

- (Resolved) Unsubscribe buffer policy: see ADR-0004.
- (Resolved) Conflict policy (contested planning by default, rare blocking): see ADR-0002.
