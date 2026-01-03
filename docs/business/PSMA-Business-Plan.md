# Program Subscription Manager Application (PSMA) — Business Plan

## Executive summary
Program Subscription Manager Application (PSMA) helps users manage streaming subscriptions based on the *programs they want to watch* rather than the streaming services they happen to be subscribed to.

The core outcome PSMA provides is a **subscription plan**: a schedule of when to subscribe and unsubscribe from streaming services so the user can watch selected shows while minimizing unnecessary subscription time and costs.

PSMA is designed as a low-cost, local-first MVP for internal trial users in the United States, with an architecture that can be extended to incorporate additional data providers, user accounts/logins, and multiple UI experiences.

## Problem statement
Streaming has become increasingly fragmented:
- More studios run their own services.
- Content exclusivity changes frequently.
- Shows move between services over time.

As a result, users who want to watch a set of shows must repeatedly do manual work:
1. Determine *where* a show is available.
2. Determine *when* it is available (release dates; availability windows).
3. Subscribe to the right service.
4. Remember to unsubscribe when the viewing goal is complete.

This creates:
- avoidable recurring costs (“subscription creep”)
- time wasted on research and tracking
- missed releases and frustration when shows move or disappear

## Proposed solution (MVP)
PSMA enables users to subscribe to **shows** (and viewing intentions) rather than subscribing to services without a plan.

### Core MVP capabilities
- **Aggregate catalog (US):** A best-effort catalog of shows and viewing availability from multiple providers where feasible.
- **Select and manage shows:** Users save a list of shows they intend to watch.
- **Viewing preferences:** Users specify how they want to watch:
  - watch as new episodes are available (weekly / “as aired”)
  - binge after the season is complete
- **Plan generation:** PSMA creates a recommended timeline of subscribe/unsubscribe actions across services.
- **Reminders + instructions:** PSMA notifies the user of upcoming subscribe/unsubscribe actions.
  - MVP is confirmation-based: “here’s what to do and when.”

### What MVP does not do
To keep cost and complexity low, MVP will not:
- automatically subscribe/unsubscribe on the user’s behalf
- guarantee 100% coverage of all streaming services (coverage improves over time via provider expansion)

## Target users (initial)
- Internal pilot users in the US who subscribe to multiple streaming services intermittently.
- Households trying to reduce streaming spend without giving up access to preferred shows.

## Value proposition
### For users
- Spend less by subscribing only when needed.
- Spend less time researching availability and release dates.
- Receive proactive guidance when data changes.

### For the product
- Differentiated positioning: “subscription planning” rather than only “where to watch.”
- Extensible architecture: supports more providers and features without redesign.

## Competitive landscape (high-level)
There are widely used tools for parts of this workflow:
- discovery and “where to watch” aggregation
- watch tracking
- general subscription management

PSMA differentiates by combining:
- show-first planning
- user-preference-driven timing optimization
- proactive change detection and guidance

## Feasibility and constraints
### What is straightforward
- The planning logic (generate a schedule from availability windows and user preferences).
- A simple UI to select shows and view a plan.
- A reminder/export mechanism (e.g., calendar export) with no ongoing service costs.

### What is difficult (and why the strategy matters)
- Comprehensive, accurate “where to watch” availability data across all services is often commercial and/or restricted.
- Release dates can be unknown or shift.

Therefore the MVP strategy is:
- operate on best-effort data for internal trials
- clearly label sources and confidence
- design a multi-provider system so coverage and quality improve over time

## Product approach: local-first and low-cost
### Operating model
- MVP can run standalone.
- Data is stored locally.
- Users can run it without accounts/logins.

### “Future-aware” security
Even though MVP is single-user, the system will be designed to support:
- user accounts/logins later (securely)
- multi-user separation of data
- role-based workflows and audit trails for AI-assisted suggestions

## Data and provider strategy
### Multi-provider architecture
PSMA is designed to incorporate several providers. Providers can differ in coverage and quality.

Key principles:
- providers contribute data in a normalized format
- all data is stored with provenance (who said it, when)
- the system can reconcile conflicts and ask the user when needed

### Handling data changes
Data changes are expected:
- a show moves between services
- availability windows tighten or expand
- release dates become known or change

PSMA will:
- detect changes
- evaluate whether the user’s plan is affected
- prompt the user if a decision is needed

## AI strategy (role-based, confirmation-first)
PSMA uses AI as a guidance engine rather than an unquestioned source of truth.

### What AI does
- Personalizes recommendations using what is known about the user (preferences, prior decisions, constraints).
- Interprets changes in data and explains what matters.
- Asks targeted questions to resolve ambiguity.

Example:
- If a service typically releases full seasons at once, PSMA can suggest bingeing rather than “watch weekly” to reduce subscription time.

### Guardrails
- AI suggestions are not applied automatically in MVP.
- AI outputs are transparent and explainable.
- The system stores the rationale for suggestions.

### “Agent bios” (role-based behavior)
The AI engine supports different roles depending on the task:
- Scheduler: focuses on timing and minimizing time subscribed.
- Researcher: focuses on resolving unknown dates/conflicting sources.
- (Future) Safety advisor: answers household suitability questions when ratings data is available.

## MVP scope, success criteria, and metrics
### MVP scope (internal pilot)
- US region
- multi-provider ingestion (at least one free provider + a manual import option)
- show selection + preference setting
- plan generation + plan review
- reminders/instructions with confirmation

### Success criteria
- Users can reliably create a plan from their selected shows.
- Users understand why the plan recommends certain actions.
- Users report reduced time spent managing subscriptions.
- Users report fewer “forgot to cancel” events.

### Suggested pilot metrics
- average number of active subscriptions per user over time
- number of times the plan changes due to data updates
- number of AI prompts that result in confirmed preference changes
- self-reported cost savings (directional; not guaranteed)

## Risks and mitigations
### Data coverage risk
- Risk: free providers may not cover all services.
- Mitigation: best-effort messaging, provenance labeling, manual override/import, multi-provider expansion.

### Data quality/conflict risk
- Risk: providers disagree or are stale.
- Mitigation: conflict detection, confidence scoring, user confirmation flow.

### Trust risk (AI)
- Risk: users distrust AI recommendations.
- Mitigation: confirmation-first UX, explain rationale, keep deterministic planner authoritative.

### Legal/terms-of-service risk
- Risk: certain data collection methods may violate terms.
- Mitigation: favor approved APIs and user-provided keys; avoid scraping as default.

## Roadmap
### Phase 1: Internal MVP (core value)
- Catalog ingestion (multi-provider)
- Selection + preferences
- Plan generation
- Confirmation-based reminders

### Phase 2: Provider expansion and higher fidelity planning
- Add providers to improve coverage
- Improve pricing/billing assumptions
- Improve release-date research workflow

### Phase 3+: Automation and advanced experiences (optional)
- Optional subscription automation where feasible
- Additional UIs (mobile, browser extension, etc.)
- Household suitability features (ratings providers + safety advisor)

## Open-source strategy
The project is intended to keep the core as open-source as possible:
- core planning engine and data model
- provider interfaces (ports)
- basic UI

Adapters that require proprietary keys or special licensing can remain separate modules while still integrating cleanly through the same interfaces.
