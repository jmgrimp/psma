# How PSMA Uses AI (Safely) — Non-Technical

## What AI does in PSMA

PSMA uses AI to help a user make better decisions when:
- streaming availability changes
- a provider’s data is missing or ambiguous
- a user’s preferences conflict with known service behavior

AI is used to **explain** and to **ask targeted questions**, not to replace the user’s judgment.

## What AI does NOT do

In MVP, AI does not:
- automatically subscribe/unsubscribe to services
- silently change your preferences
- silently change catalog facts (“where to watch”)
- invent dates or availability claims

## Confirmation-based by design

AI can propose:
- a recommendation (e.g., “binge after the season to reduce subscription time”)
- a conflict resolution suggestion (e.g., “two sources disagree; which service do you want to assume?”)
- a clarifying question (e.g., “how long do you plan to stay subscribed?”)

But **nothing changes** until the user confirms.

## Why AI advice can be trusted (within limits)

PSMA keeps AI grounded by using:
- your **confirmed preferences**
- provider **provenance** (where a fact came from and when)
- a small curated “service behavior knowledge base” (SBKB), such as whether a service typically releases entire seasons at once

PSMA also keeps uncertainty visible via confidence signals.

## Roles (simple mental model)

PSMA uses two “modes” of AI behavior:
- **Scheduler:** focuses on planning tradeoffs and reminders.
- **Researcher:** focuses on resolving unknowns and conflicts.

(Other roles, like safety/suitability guidance, are future scope and require additional data sources.)

## What happens when data changes

When a refresh changes something that affects your plan:
- PSMA computes what changed and how it impacts your plan
- AI explains the impact and suggests what to do next
- you confirm or decline
- PSMA updates the plan and reminders

## Source of truth

This document is based on:
- [docs/technical/13-AI-Policies-and-Workflows.md](../technical/13-AI-Policies-and-Workflows.md)
- [docs/technical/03-AI-Agent-System.md](../technical/03-AI-Agent-System.md)
