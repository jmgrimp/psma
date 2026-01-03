# User Stories (MVP + Future) — WIP

This document is a living backlog. Stories will be added, split, and refined as we learn from internal trials and provider constraints.

This document defines user stories for PSMA in a form suitable for engineering planning.

## Status

- **WIP:** Do not treat as complete or final.
- Stories may be re-scoped between MVP and later phases.

## How to use this document

- Use the **Acceptance criteria** as the source of truth for “done.”
- Prefer adding new stories over overloading existing ones.
- When a story becomes implementation-ready, add explicit assumptions and remove ambiguity.

## Conventions

- **Actor**: who wants the capability
- **Story**: user-level intent
- **Acceptance criteria**: verifiable outcomes
- **Notes**: assumptions and non-goals

## Personas (technical)

- **Viewer**: selects shows and wants a subscription plan.
- **Power Viewer**: has constraints (budget, avoid overlap, binge preference).
- **Admin/Operator** (future): manages tenants, provider configuration, and monitoring.
- **Developer**: adds providers/LLM adapters and tests contracts.

---

## Epic A — Catalog aggregation (US)

### A1 (MVP): Browse available and upcoming shows
- **Actor**: Viewer
- **Story**: As a viewer, I want to browse a catalog of shows so I can discover and select what to watch.
- **Acceptance criteria**
  - Catalog view lists shows with a status (available/upcoming/unknown).
  - Each show includes at least title and source provenance (provider and retrieval time).
  - Catalog is filtered to US region (explicitly shown).

### A2 (MVP): Refresh catalog from multiple providers
- **Actor**: Viewer
- **Story**: As a viewer, I want to refresh the catalog so I can see the latest availability.
- **Acceptance criteria**
  - Refresh pulls from all enabled providers.
  - Imported facts are stored with provenance (provider id, retrieved_at, confidence).
  - The system produces a merged canonical view and records conflicts.

### A3 (MVP): See provider conflicts
- **Actor**: Viewer
- **Story**: As a viewer, I want to see when providers disagree so I can resolve uncertainty.
- **Acceptance criteria**
  - Conflicts are visible and tied to the affected show/service.
  - Each conflict displays the competing values and their provenance.
  - User can choose a resolution (manual confirmation) or defer.

### A4 (Future): Coverage and confidence indicators
- **Actor**: Viewer
- **Story**: As a viewer, I want to know how complete and trustworthy the catalog is so I can decide what to trust.
- **Acceptance criteria**
  - Coverage summary per provider and service is displayed.
  - Items with low confidence are clearly marked.

---

## Epic B — Manage show selections and preferences

### B1 (MVP): Select a show to watch
- **Actor**: Viewer
- **Story**: As a viewer, I want to add a show to my list so PSMA can plan subscriptions for me.
- **Acceptance criteria**
  - User can add a show to “My Shows”.
  - The selection is persisted and survives restart.

### B2 (MVP): Choose how to watch (weekly vs binge)
- **Actor**: Viewer
- **Story**: As a viewer, I want to specify whether I’ll watch weekly or binge so the plan matches my behavior.
- **Acceptance criteria**
  - User can set watch mode per show: `as_aired` or `binge_after_season`.
  - If binge mode, user can set a binge duration (days).

### B3 (MVP): Update or remove a selection
- **Actor**: Viewer
- **Story**: As a viewer, I want to update/remove shows so the plan stays accurate.
- **Acceptance criteria**
  - User can remove a show from “My Shows”.
  - User can change preferences and changes are reflected in the next plan generation.

### B4 (Future): Household constraints
- **Actor**: Power Viewer
- **Story**: As a power viewer, I want to define constraints (budget, max concurrent subscriptions, avoid ad tiers) so PSMA optimizes accordingly.
- **Acceptance criteria**
  - Constraints can be saved per user.
  - Planner and/or AI uses constraints when proposing changes.

---

## Epic C — Plan generation (deterministic)

### C1 (MVP): Generate a subscription instruction plan
- **Actor**: Viewer
- **Story**: As a viewer, I want PSMA to generate a subscribe/unsubscribe schedule so I can watch my selected shows while minimizing wasted subscription time.
- **Acceptance criteria**
  - Plan output includes dated events: subscribe/unsubscribe per service.
  - Each event includes a human-readable rationale.
  - Planner behavior is deterministic given the same inputs.
  - Plan clearly states any assumptions (e.g., unknown availability end dates).

### C2 (MVP): Show a plan delta when data changes
- **Actor**: Viewer
- **Story**: As a viewer, I want to see what changed in my plan after a refresh so I can decide whether to adopt updates.
- **Acceptance criteria**
  - System computes a plan delta (added/removed events and date shifts).
  - Delta is understandable without reading raw data.

### C3 (Future): Optimize by billing-cycle and pricing
- **Actor**: Power Viewer
- **Story**: As a power viewer, I want PSMA to account for pricing and billing cycles so the plan is cost-optimized, not just time-optimized.
- **Acceptance criteria**
  - Pricing assumptions are explicit.
  - Planner supports alternative strategies (e.g., subscribe at month boundary).

---

## Epic D — Reminders and execution

### D1 (MVP): Provide reminders without automation
- **Actor**: Viewer
- **Story**: As a viewer, I want reminders for subscribe/unsubscribe events so I don’t forget.
- **Acceptance criteria**
  - User can view upcoming events.
  - User can export reminders (e.g., calendar export) OR receive in-app reminders.
  - No automatic subscription actions occur in MVP.

### D2 (Future): Optional automation
- **Actor**: Viewer
- **Story**: As a viewer, I want PSMA to optionally automate subscribe/unsubscribe actions.
- **Acceptance criteria**
  - Automation is opt-in.
  - Actions are auditable.
  - System clearly states service limitations/constraints.

---

## Epic E — AI guidance (role-based, confirmation-first)

### E1 (MVP): AI suggests preference improvements based on service behavior
- **Actor**: Viewer
- **Story**: As a viewer, I want PSMA to warn me when my selected preference is likely suboptimal given known service behaviors.
- **Acceptance criteria**
  - System uses SBKB facts (e.g., release pattern) to detect advice opportunities.
  - AI generates a recommendation explaining the tradeoff.
  - User can accept or decline the suggested preference change.

### E2 (MVP): AI asks targeted questions when ambiguity blocks planning
- **Actor**: Viewer
- **Story**: As a viewer, I want PSMA to ask the smallest number of questions needed to keep my plan accurate.
- **Acceptance criteria**
  - Questions are tied to a specific conflict/unknown.
  - Answering questions updates preferences or conflict resolutions.
  - System does not silently change preferences or facts without confirmation.

### E3 (Future): Researcher role for unknown dates/conflicts
- **Actor**: Viewer
- **Story**: As a viewer, I want PSMA to research unknown dates and conflicting sources so I don’t have to.
- **Acceptance criteria**
  - Research outputs include provenance/citations.
  - Suggested updates are confirmation-based.

### E4 (Future): Safety/age suitability questions
- **Actor**: Viewer
- **Story**: As a viewer, I want to ask if a show is suitable for a child of a given age.
- **Acceptance criteria**
  - System uses a ratings/content descriptor provider.
  - Answers cite the rating/descriptors.
  - If data is missing, system returns “unknown” and explains what’s missing.

---

## Epic F — Multi-tenancy and identity (future-aware)

### F1 (MVP): Single-user mode with future-ready scoping
- **Actor**: Viewer
- **Story**: As a viewer, I want to use PSMA without setting up accounts.
- **Acceptance criteria**
  - App runs in single-user mode.
  - Internal data model is user-scoped (default user/tenant) so login can be added later.

### F2 (Future): Secure login and tenant isolation
- **Actor**: Viewer
- **Story**: As a viewer, I want secure login so my preferences and plans are private.
- **Acceptance criteria**
  - Authentication is enforced at API boundary.
  - All tenant-scoped data is isolated by `tenant_id`.
  - Users cannot access other tenants’ data.

---

## Epic G — Developer and operations

### G1 (MVP): Configure providers and LLM at runtime
- **Actor**: Developer
- **Story**: As a developer, I want to select providers and LLM configuration without code changes so I can experiment.
- **Acceptance criteria**
  - Providers can be enabled/disabled via configuration.
  - LLM adapter can be configured (e.g., OpenRouter base URL + model + key).
  - The app runs without an LLM (stub) in development.

### G2 (MVP): Contract tests for providers and AI outputs
- **Actor**: Developer
- **Story**: As a developer, I want contract tests so new providers/agents don’t break the system.
- **Acceptance criteria**
  - Provider outputs are validated against JSON schema.
  - AI outputs are validated against JSON schema.
  - CI fails on contract mismatch.

### G3 (Future): Observability
- **Actor**: Admin/Operator
- **Story**: As an operator, I want to monitor refresh/job status and error rates.
- **Acceptance criteria**
  - Refresh history is visible.
  - Provider failures and rate limiting are recorded.
  - Job status is queryable.
