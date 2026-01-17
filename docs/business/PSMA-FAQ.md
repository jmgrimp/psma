# PSMA — FAQ (Non-Technical)

## What is PSMA?
PSMA (Program Subscription Manager Application) helps users manage streaming subscriptions based on *shows they want to watch*.

## How is this different from “where to watch” apps?
Most tools tell you where a show is available.

PSMA uses that information plus your viewing preferences to produce a **subscription schedule** (when to subscribe and unsubscribe) so you can watch what you want while minimizing unnecessary subscription time.

## Will it really include every show from every service?
That is the long-term goal, but in the MVP we treat coverage as **best effort**.

Availability data can be restricted, region-specific, and changes frequently. PSMA is designed to support multiple providers so coverage improves over time.

## Does PSMA subscribe/unsubscribe for me?
Not in MVP.

MVP provides instructions and reminders. Automation may be explored in later phases where feasible.

## How does PSMA handle changes (shows move, dates change)?
PSMA periodically refreshes availability data, detects what changed, and determines whether your plan is impacted.

If the plan could change, PSMA will:
- explain what changed
- recommend an updated plan
- ask you to confirm

## What does the AI do?
AI provides guidance and asks smart questions when the system detects ambiguity or changes.

Examples:
- If your chosen viewing preference doesn’t match how a service typically releases content, PSMA can suggest a cheaper plan.
- If two data sources disagree about where a show is available, PSMA can ask you to confirm.

AI suggestions are confirmation-based.

## Is the system expensive to run?
The MVP is designed to be low-cost and can run standalone.

## Will it have logins?
MVP is single-user for internal trial simplicity, but the architecture is designed to support secure login and multi-user environments later.

## How will we add more services and data sources?
PSMA is built to incorporate multiple “providers.” Providers can be added over time to improve coverage and data quality.

## Why isn’t a live TV bundle (like YouTube TV) listed as “where to watch” for a show?
Many “where to watch” sources focus on on-demand libraries.

Live TV bundles work differently:
- Access depends on your local lineup (networks/channels) and current/recent airings.
- Title-level “available on Service X” data is often missing or not comparable to on-demand data.

In PSMA MVP, the practical approach is:
- treat your live bundle as a **permanent service** (always-on)
- let PSMA plan add-on subscriptions around it

Over time, PSMA can become smarter about live bundles by incorporating lineup and airing data.
