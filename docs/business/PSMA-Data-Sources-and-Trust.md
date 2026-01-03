# PSMA Data Sources & Trust (Non-Technical)

## What this document is

PSMA combines streaming availability information from one or more sources (“providers”). This explains what that means, how trustworthy the results are, and how PSMA handles disagreements.

## What data PSMA uses

PSMA needs two main kinds of information:
- **Show identity and metadata:** the title, season/episode structure, and identifiers.
- **Availability windows:** where and when a show is streamable (for the US in MVP).

PSMA is designed to support multiple providers over time.

## Best-effort coverage (important)

MVP coverage is **best-effort**, not guaranteed.
- Some services may be missing.
- Some dates may be unknown.
- Providers may disagree.

PSMA treats these limitations as normal and makes them visible rather than hiding them.

## Provenance and confidence

When PSMA shows an availability claim, it keeps track of:
- **Where it came from** (provider name)
- **When it was retrieved**
- **How confident PSMA is** (a simple confidence signal)

This allows PSMA to explain “why” it believes something and to show uncertainty when needed.

## When providers disagree (conflicts)

Sometimes one provider says a show is on Service X, while another says Service Y.

PSMA handles this by:
- **recording a conflict** (instead of pretending one source is always right)
- producing a plan that can still be useful, but labeling affected plan items as **contested**
- asking the user to confirm a resolution when it matters

In rare cases where the conflict makes planning unsafe, PSMA will:
- generate a partial plan for unaffected shows
- ask a clear question to unblock the specific show

## Deterministic tie-breakers (for consistency)

When a show appears to be available on multiple services, PSMA needs a consistent default choice.

MVP tie-breakers are:
- prefer higher-confidence facts
- then prefer more recently retrieved facts
- then use a stable ordering (so the result is repeatable)

PSMA still records that alternatives existed.

## Missing end dates (unknown “available until”)

Many sources can’t reliably tell when a show will stop being available.

PSMA does **not** silently invent a date.
Instead, it:
- marks the end date as unknown
- uses a conservative default planning horizon (and labels it as an assumption)
- may ask a user how long they expect to keep the subscription if it affects cost/overlap

## Manual import (so the MVP always works)

MVP includes a **manual import option** (CSV/JSON) so a pilot user can:
- add a show
- specify the service
- specify an availability window

This ensures the app remains usable even if external providers are incomplete.

## Terms of use and constraints

PSMA will only use providers whose terms are acceptable for the intended deployment.
Provider selection is a deliberate decision and may change over time.

## Source of truth

This document is based on:
- [docs/technical/12-Provider-Data-Plan.md](../technical/12-Provider-Data-Plan.md)
- [docs/technical/ADR-0002-Conflict-Handling-Policy.md](../technical/ADR-0002-Conflict-Handling-Policy.md)
- [docs/technical/ADR-0003-Unknown-Availability-End-Date-Policy.md](../technical/ADR-0003-Unknown-Availability-End-Date-Policy.md)
- [docs/technical/ADR-0004-Deterministic-TieBreakers-and-Buffers.md](../technical/ADR-0004-Deterministic-TieBreakers-and-Buffers.md)
