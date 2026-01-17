# Contracts

This folder contains stable, versionable contracts shared across components.

## OpenAPI

- `contracts/openapi/psma.openapi.json` is the generated OpenAPI document for the backend.
- Generate/update it via: `pnpm gen:openapi`

## JSON Schema

- `contracts/jsonschema/` contains versioned JSON Schemas for internal contracts (provider outputs, engine outputs).

## Registries

- `contracts/registry/` contains curated registries used for normalization (e.g., mapping external provider IDs to canonical `service_id`).
