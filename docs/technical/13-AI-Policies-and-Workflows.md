# AI Policies, Roles, and Workflows — WIP

This document defines how AI is used in PSMA without making AI the source of truth.

## 1. AI goals

- Provide intelligent guidance based on:
  - user preferences and confirmed facts
  - known service behaviors (SBKB)
  - changes in availability/release dates
- Ask targeted questions when ambiguity blocks planning.

## 2. Guardrails (non-negotiable)

- AI is advisory and confirmation-based.
- AI must not invent catalog facts.
- Any data-driven claim must reference provenance where possible.
- Any preference change must be user-confirmed.

## 3. Roles (“agent bios”)

### Scheduler
- Focus: planning and preference tradeoffs.
- Inputs: preferences, constraints, plan delta, SBKB.
- Outputs: recommendations + minimal questions.

### Researcher
- Focus: resolving unknowns and conflicts.
- Inputs: conflicts, missing dates, provider facts.
- Outputs: suggested resolutions with confidence and references.

### Safety advisor (future)
- Focus: suitability questions.
- Requires: ratings/content descriptor provider.

## 4. Service Behavior Knowledge Base (SBKB)

SBKB stores curated facts about services.

Minimum schema:
- `service_id`
- `release_pattern`: all_at_once | weekly | mixed | unknown
- `confidence`
- `source_ref`
- `notes`

SBKB is a fact source; the AI uses SBKB rather than relying on model “memory.”

## 5. AI trigger conditions

AI runs when:
- a refresh produces a user-impacting change
- a conflict affects a selected show
- a preference conflicts with SBKB (e.g., all-at-once service + as-aired preference)

## 6. AI outputs (structured)

AI must output a structured object that includes:
- `recommendations[]`
  - type: preference_change | conflict_resolution | plan_explanation
  - summary
  - details
  - confidence
  - based_on (facts and/or SBKB entries)
- `questions[]`
  - prompt
  - why_needed
  - options (optional)
- `explanation`

## 7. Confirmation workflow

1) System computes plan delta.
2) AI produces explanation + recommendations + questions.
3) UI presents:
   - what changed
   - what is recommended
   - what questions must be answered
4) User confirms/declines.
5) System applies confirmed updates and regenerates plan.

## 8. Memory policy (user knowledge)

Maintain a clear separation:
- **Confirmed facts**: explicit user settings and explicit user confirmations.
- **Inferred preferences**: AI suggestions not yet confirmed.

Rules:
- Only confirmed facts affect planning.
- Inferred preferences may be used to propose questions/recommendations.

## 9. LLM provider configurability

- LLM adapters are chosen by configuration.
- Must support OpenAI-compatible APIs (OpenRouter) via:
  - configurable base URL
  - configurable model
  - configurable API key

## 10. Open questions

- Do we store full conversation transcripts or only structured summaries?
- What is the minimum audit log we require for AI recommendations?
