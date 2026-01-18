from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from psma_api.models.availability import AvailabilityAssessmentV1


PlanActionV1 = Literal["subscribe", "unsubscribe"]


class PlanningInputV1(BaseModel):
    key: str = Field(
        ..., min_length=1, description="Stable input key. New keys may be added without changing the envelope shape."
    )
    value: Any
    service_id: str | None = Field(default=None, min_length=1, description="Optional service scope for the input.")
    title_ids: list[str] | None = Field(default=None, description="Optional title scope for the input.")
    source_id: str | None = Field(
        default=None, min_length=1, description="Optional provenance identifier (e.g., ui, import, ai_suggested)."
    )
    collected_at: datetime | None = Field(default=None, description="When this input was collected (optional).")
    notes: str | None = Field(default=None, description="Optional human-readable notes.")

    model_config = {"extra": "forbid"}


class PlanQuestionV1(BaseModel):
    id: str = Field(..., min_length=1, description="Stable identifier for de-duplication and UI tracking.")
    key: str = Field(
        ..., min_length=1, description="Stable question key. New keys may be added without changing the envelope shape."
    )
    prompt: str = Field(..., min_length=1)
    required: bool
    service_id: str | None = Field(default=None, min_length=1, description="Optional service scope for the question.")
    title_ids: list[str] | None = Field(default=None, description="Optional title scope for the question.")
    answer_schema: dict[str, Any] | None = Field(
        default=None, description="Optional JSON Schema fragment describing the expected answer."
    )
    rationale: str | None = Field(default=None, description="Optional explanation of why this question matters.")

    model_config = {"extra": "forbid"}


class PlanRequestV1(BaseModel):
    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    assessments: list[AvailabilityAssessmentV1]
    permanent_service_ids: list[str] = Field(default_factory=list)
    horizon_days: int = Field(default=30, ge=1, le=365)
    inputs: list[PlanningInputV1] = Field(
        default_factory=list,
        description="Optional open-ended planner inputs (user preferences, constraints, derived estimates).",
    )

    model_config = {"extra": "forbid"}


class PlanEventV1(BaseModel):
    action: PlanActionV1
    service_id: str = Field(..., min_length=1)
    effective_at: datetime
    reason_codes: list[str] = Field(..., min_length=1)
    title_ids: list[str] = Field(..., min_length=1)
    assumptions: list[str] | None = None

    model_config = {"extra": "forbid"}


class PlanResponseV1(BaseModel):
    generated_at: datetime
    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    horizon_days: int = Field(..., ge=1, le=365)
    events: list[PlanEventV1]
    questions: list[PlanQuestionV1] | None = None

    model_config = {"extra": "forbid"}
