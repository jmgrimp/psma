# Service Identity and Registry

This document defines how PSMA identifies “services” (e.g., Netflix, YouTube TV) consistently across providers and engines, and how services are classified for planning.

## Goals

- Provide a stable `service_id` used everywhere in PSMA.
- Map multiple external identifiers (TMDB provider IDs, vendor slugs, etc.) onto a single `service_id`.
- Enable a user service profile (including permanent services) without ambiguity.
- Make it easy to add new services without changing core engine/planner logic.

## Non-goals

- Solving every tier/plan variant (e.g., “Basic with Ads” vs “Premium”) in v1.
- Tracking real-time pricing; pricing is treated as a time-bound fact.

## Terminology

- **Service**: a consumer-facing service the user subscribes to (Netflix, Max, YouTube TV).
- **Provider (adapter)**: an integration source that supplies facts (TMDB watch providers, TVmaze, manual import, etc.).
- **External ID**: a provider-specific identifier for a service (e.g., TMDB provider_id).

## Canonical `service_id`

- `service_id` is an internal identifier, stable and provider-agnostic.
- Recommended format: lowercase kebab-case (e.g., `netflix`, `youtube-tv`, `apple-tv-plus`).
- `service_id` must not embed region/tier unless PSMA explicitly models tiers.

### Why not use TMDB provider_id as canonical?

- TMDB coverage is incomplete for some services (especially live bundles).
- Some services have multiple representations/brands across sources.
- We want to keep the system usable even if TMDB is disabled.

## External ID mapping rules

PSMA should maintain a registry that maps external IDs to `service_id`.

- Each service entry can map multiple external IDs.
- Mapping is many-to-one (many external IDs → one `service_id`).
- If a provider returns an unknown external ID, PSMA should:
  - create an “unknown service” placeholder in the canonical view, and/or
  - record a conflict and prompt for operator/user confirmation (depending on UX policy).

## Service categories (for planning)

A service has a primary category:
- `svod` — subscription on-demand library
- `avod` — ad-supported on-demand
- `tvod` — transactional rent/buy
- `live_bundle` — live TV bundle/aggregator
- `unknown`

Notes:
- Category drives interpretation of availability and planning.
- Category is *not* derived solely from monetization type in upstream data; it can be curated with overrides.

## User service profile

Users can record which services they already have.

- A user may mark a service as `permanent` (always-on).
- The planner must not generate subscribe/unsubscribe events for permanent services.
- Permanent services can still satisfy availability constraints and reduce the need for add-on subscriptions.

## Pricing

Pricing can be used as a tie-breaker, but must be treated as time-bound:
- prices are facts with provenance and `retrieved_at`
- prices may be non-comparable across tiers/billing cycles

## Registry location and lifecycle

- The service registry is a curated artifact (checked into the repo) and can be extended incrementally.
- Future: allow per-tenant overrides or user overrides, still mapping to canonical `service_id`.

Registry:
- [contracts/registry/service-registry.v1.json](../../contracts/registry/service-registry.v1.json)

Related:
- [contracts/jsonschema/availability/availability-assessment.v1.schema.json](../../contracts/jsonschema/availability/availability-assessment.v1.schema.json)
- [docs/technical/18-Availability-Engine.md](18-Availability-Engine.md)
- [docs/technical/ADR-0004-Deterministic-TieBreakers-and-Buffers.md](ADR-0004-Deterministic-TieBreakers-and-Buffers.md)
