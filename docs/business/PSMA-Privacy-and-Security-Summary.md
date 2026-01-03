# PSMA Privacy & Security Summary (Non-Technical)

## MVP posture

PSMA MVP is designed for internal pilot use and can run **standalone**.

Even in MVP, PSMA is designed so security and user separation can be added later without a redesign.

## Data PSMA stores

PSMA aims to store the minimum needed to function:
- your selected shows and viewing preferences
- your generated plan and reminders
- “where to watch” facts and their provenance (where/when retrieved)
- an audit trail of confirmations/declines for AI suggestions and conflict resolutions

## Local-first by default

In standalone mode:
- data is stored locally (e.g., in a local database)
- reminders may be generated as a calendar export

This keeps operating costs low and reduces the need to send user data to a server.

## Future hosted mode (later)

If PSMA becomes hosted:
- authentication can be added at the API boundary (e.g., single sign-on)
- user/tenant data is isolated logically (so one user/tenant can’t see another)

## AI-related auditability

Because AI guidance is advisory and confirmation-based:
- PSMA records what was suggested
- PSMA records what the user confirmed or declined

This helps with transparency and debugging.

## Secrets (API keys)

Provider keys (including AI provider keys) must not be stored in source control.
They will be configured using environment variables or appropriate secret storage.

## Source of truth

This document is based on:
- [docs/technical/05-Security-and-Identity.md](../technical/05-Security-and-Identity.md)
- [docs/technical/ADR-0001-Backend-Stack-and-MultiTenancy.md](../technical/ADR-0001-Backend-Stack-and-MultiTenancy.md)
