# PSMA MVP Examples (Non-Technical)

These examples illustrate what PSMA produces and how it behaves in common situations.

## Example: One show on one service
- You choose a show.
- PSMA shows where it’s available and for what dates.
- PSMA produces a plan: “subscribe on X date; unsubscribe shortly after the show is no longer available.”

## Example: Two shows on the same service
- You choose two shows that overlap on the same service.
- PSMA produces one combined subscription window (so you don’t subscribe twice).

## Example: Missing “end date” for availability
- A provider can’t tell when a show will leave a service.
- PSMA labels the end date as unknown.
- PSMA still produces a usable plan using a conservative default assumption, and may ask how long you expect to keep the subscription if it matters.

## Example: Providers disagree (“conflict”)
- One source says the show is on Service X.
- Another source says the show is on Service Y.
- PSMA records the disagreement and will either:
  - produce a plan with a **contested** label and ask you to confirm, or
  - ask a question before planning for that specific show (rare)

## Example: AI suggests a cheaper watching approach
- You choose “watch weekly,” but the service releases an entire season at once.
- PSMA’s AI suggests switching to “binge after season” because it may reduce subscription time.
- You decide whether to accept.

## Example: Plan changes after a refresh
- Availability shifts earlier/later after a refresh.
- PSMA shows what changed.
- AI explains the impact.
- You confirm/decline changes and then PSMA regenerates the plan.

## Source of truth

This document is based on:
- [docs/technical/15-Golden-Scenarios.md](../technical/15-Golden-Scenarios.md)
