from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Attribution(BaseModel):
    required: bool = True
    text: str
    url: str | None = None


class ProviderEnvelope(BaseModel):
    provider: str = Field(..., description="Provider identifier (e.g. tvmaze, tmdb)")
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When PSMA fetched this data (UTC)",
    )
    attribution: Attribution | None = None
    request: dict[str, Any] = Field(default_factory=dict)
    data: Any
