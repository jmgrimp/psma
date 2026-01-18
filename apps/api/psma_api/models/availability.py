from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


AvailabilityNowV1 = Literal["true", "false", "unknown"]
ProviderCategoryV1 = Literal["svod", "avod", "tvod", "live_bundle", "unknown"]
ConfidenceV1 = Literal["high", "medium", "low"]
CadenceV1 = Literal["weekly", "batch", "ended", "unknown"]


class AvailabilityWindowV1(BaseModel):
    start: datetime | None = Field(default=None, description="When availability is known to begin (optional).")
    end: datetime | None = Field(default=None, description="When availability is known to end (optional).")

    model_config = {"extra": "forbid"}


class EvidenceV1(BaseModel):
    source_id: str = Field(..., min_length=1)
    retrieved_at: datetime
    source_ref: str | None = None
    details: dict[str, Any] | None = None

    model_config = {"extra": "forbid"}


class PlanningHintsV1(BaseModel):
    cadence: CadenceV1 | None = None
    next_air_time: datetime | None = None
    last_air_time: datetime | None = None

    model_config = {"extra": "forbid"}


class AvailabilityAssessmentV1(BaseModel):
    title_id: str = Field(..., min_length=1)
    country: str = Field(..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    service_id: str = Field(..., min_length=1)
    provider_category: ProviderCategoryV1
    availability_now: AvailabilityNowV1
    confidence: ConfidenceV1
    reason_codes: list[str] = Field(..., min_length=1)
    evidence: list[EvidenceV1] = Field(..., min_length=1)
    availability_window: AvailabilityWindowV1 | None = None
    planning_hints: PlanningHintsV1 | None = None

    model_config = {"extra": "forbid"}


class AvailabilityAssessmentsResponseV1(BaseModel):
    retrieved_at: datetime
    assessments: list[AvailabilityAssessmentV1]

    model_config = {"extra": "forbid"}
