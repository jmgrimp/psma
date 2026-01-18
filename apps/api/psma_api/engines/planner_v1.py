from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
import math

from psma_api.models.availability import AvailabilityAssessmentV1
from psma_api.models.planning import PlanEventV1, PlanQuestionV1, PlanRequestV1, PlanResponseV1


_CONF_ORDER: dict[str, int] = {"high": 0, "medium": 1, "low": 2}
_CATEGORY_ORDER: dict[str, int] = {"svod": 0, "live_bundle": 1, "avod": 2, "tvod": 3, "unknown": 4}


def _is_plannable_service(service_id: str, assessments: list[AvailabilityAssessmentV1]) -> bool:
    # We intentionally keep unknown/unmapped providers in the *availability* output
    # (useful for debugging and registry expansion), but the planner should not
    # generate subscription events for services it cannot canonicalize.
    if service_id.startswith("unknown-"):
        return False

    # Also guard on explicit engine reason codes.
    for a in assessments:
        if any(code == "SERVICE_ID_UNKNOWN" for code in a.reason_codes):
            return False
    return True


def _pick_best_assessment(assessments: list[AvailabilityAssessmentV1]) -> AvailabilityAssessmentV1:
    # Deterministic ordering: availability_now true first, then confidence, then category.
    def key(a: AvailabilityAssessmentV1) -> tuple[int, int, int, str, str]:
        availability_rank = 0 if a.availability_now == "true" else 1
        conf_rank = _CONF_ORDER.get(a.confidence, 99)
        cat_rank = _CATEGORY_ORDER.get(a.provider_category, 99)
        return (availability_rank, conf_rank, cat_rank, a.service_id, a.title_id)

    return sorted(assessments, key=key)[0]


def _get_latest_input_value(request: PlanRequestV1, *, key: str, service_id: str) -> object | None:
    # Deterministic: last entry wins (caller controls order).
    for inp in reversed(request.inputs or []):
        if inp.key != key:
            continue
        if inp.service_id != service_id:
            continue
        return inp.value
    return None


def _get_int_input(request: PlanRequestV1, *, key: str, service_id: str) -> int | None:
    value = _get_latest_input_value(request, key=key, service_id=service_id)
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


def _get_float_input(request: PlanRequestV1, *, key: str, service_id: str) -> float | None:
    value = _get_latest_input_value(request, key=key, service_id=service_id)
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _question_id(*, key: str, service_id: str) -> str:
    return f"{service_id}:{key}"


async def generate_plan_v1(request: PlanRequestV1) -> PlanResponseV1:
    now = datetime.now(timezone.utc)

    permanent = {s.strip() for s in request.permanent_service_ids if s.strip()}

    by_service: dict[str, list[AvailabilityAssessmentV1]] = defaultdict(list)
    for a in request.assessments:
        # Defensive: ignore assessments for other countries.
        if a.country != request.country:
            continue
        by_service[a.service_id].append(a)

    events: list[PlanEventV1] = []
    questions: list[PlanQuestionV1] = []

    for service_id in sorted(by_service.keys()):
        if service_id in permanent:
            continue

        service_assessments = by_service[service_id]
        if not _is_plannable_service(service_id, service_assessments):
            continue
        best = _pick_best_assessment(service_assessments)

        # MVP behavior: if anything suggests it's available now, subscribe now.
        any_available_now = any(a.availability_now == "true" for a in service_assessments)
        if not any_available_now:
            continue

        title_ids = sorted({a.title_id for a in service_assessments})
        reason_codes = sorted({code for a in service_assessments for code in a.reason_codes})

        subscribe_at = now

        subscribe_assumptions = [
            "availability_is_best_effort_snapshot",
            "billing_cycle_assumed_day_granularity",
        ]

        events.append(
            PlanEventV1(
                action="subscribe",
                service_id=service_id,
                effective_at=subscribe_at,
                reason_codes=reason_codes or best.reason_codes,
                title_ids=title_ids,
                assumptions=subscribe_assumptions,
            )
        )

        # Unsubscribe scheduling (optional): requires explicit inputs.
        # Keys are intentionally open-ended: the envelope supports adding new keys later.
        min_contract_days = _get_int_input(request, key="min_contract_days", service_id=service_id)
        estimated_watch_days = _get_float_input(request, key="estimated_watch_days", service_id=service_id)

        missing: list[str] = []
        if min_contract_days is None or min_contract_days <= 0:
            missing.append("min_contract_days")
        if estimated_watch_days is None or estimated_watch_days <= 0:
            missing.append("estimated_watch_days")

        if not missing:
            total_days = max(int(min_contract_days), int(math.ceil(float(estimated_watch_days))))
            unsubscribe_at = subscribe_at + timedelta(days=total_days)

            # Only emit within the requested planning horizon.
            if unsubscribe_at <= now + timedelta(days=int(request.horizon_days)):
                unsubscribe_reason_codes = sorted(set(reason_codes + ["UNSUBSCRIBE_SCHEDULED"]))
                events.append(
                    PlanEventV1(
                        action="unsubscribe",
                        service_id=service_id,
                        effective_at=unsubscribe_at,
                        reason_codes=unsubscribe_reason_codes,
                        title_ids=title_ids,
                        assumptions=[
                            "unsubscribe_based_on_user_inputs",
                            "min_contract_days_used",
                            "estimated_watch_days_used",
                        ],
                    )
                )
        else:
            # Return structured questions so the caller can gather the missing inputs.
            for miss in missing:
                if miss == "min_contract_days":
                    questions.append(
                        PlanQuestionV1(
                            id=_question_id(key=miss, service_id=service_id),
                            key=miss,
                            prompt=f"What is the minimum contract/billing period (in days) for {service_id}?",
                            required=True,
                            service_id=service_id,
                            answer_schema={"type": "integer", "minimum": 1},
                            rationale="Needed to avoid scheduling an unsubscribe earlier than allowed.",
                        )
                    )
                elif miss == "estimated_watch_days":
                    questions.append(
                        PlanQuestionV1(
                            id=_question_id(key=miss, service_id=service_id),
                            key=miss,
                            prompt=f"Roughly how many days will you take to watch what you want on {service_id}?",
                            required=True,
                            service_id=service_id,
                            answer_schema={"type": "number", "minimum": 0.1},
                            rationale="Needed to estimate when you can unsubscribe without missing content.",
                        )
                    )

    # De-duplicate questions deterministically.
    by_qid: dict[str, PlanQuestionV1] = {}
    for q in questions:
        by_qid[q.id] = q
    questions_out = [by_qid[qid] for qid in sorted(by_qid.keys())]

    return PlanResponseV1(
        generated_at=now,
        country=request.country,
        horizon_days=request.horizon_days,
        events=events,
        questions=questions_out or None,
    )
