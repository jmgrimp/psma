# Program Subscription Manager Application (PSMA) — One-Pager

## What it is
PSMA is a lightweight application that helps people manage streaming subscriptions based on the *shows they want to watch*—not the streaming services themselves.

Instead of subscribing to multiple services “just in case,” PSMA creates a simple, personalized plan that tells a user:
- what to subscribe to
- when to subscribe
- when to unsubscribe

## The problem
Streaming has fragmented across many services. Today, people who want to watch a set of shows must manually:
- figure out where each show is available
- track when new seasons/episodes release
- subscribe to the right service at the right time
- remember to cancel when they’re done

This creates unnecessary cost, time spent researching, and frequent “subscription creep” (paying for services you’re not using).

## The solution (MVP)
PSMA provides:
- A single place to view a best-effort catalog of shows available in the US (from multiple free data sources where possible).
- A way to select shows and choose how you want to watch them (e.g., weekly as episodes release vs binge after a season completes).
- A recommended subscription schedule that minimizes time subscribed while matching user preferences.
- Reminders/instructions for subscribing and unsubscribing (MVP: confirmation-based; no automation).

## Why it’s different
Most “where to watch” apps tell you where content is available.

PSMA goes further by:
- planning *subscription timing* across services
- adapting recommendations to the user’s preferences
- surfacing changes over time (availability, dates) and prompting the user when decisions are needed

## How AI is used (responsibly)
PSMA uses an AI assistant to provide guidance and ask smart questions when circumstances change.

Example:
- If a user chooses “watch weekly” for a service known to drop entire seasons at once, PSMA can suggest bingeing to save money.

AI is advisory and confirmation-based:
- It proposes changes.
- The user confirms.

## Deployment and budget approach
- MVP is designed to run standalone (local-first) with minimal operating costs.
- It can be extended later to support logins and multi-user environments securely.

## Roadmap
- Phase 1 (Internal MVP): show selection + plan generation + reminders + multi-provider architecture.
- Phase 2: add more providers, better pricing models, improved data freshness workflows.
- Phase 3+: optional subscription automation (where feasible) and additional UIs.
