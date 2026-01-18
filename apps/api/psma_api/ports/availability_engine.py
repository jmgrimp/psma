from __future__ import annotations

from collections.abc import Awaitable
from typing import Protocol

import httpx

from psma_api.models.availability import AvailabilityAssessmentsResponseV1


class AvailabilityEngine(Protocol):
    def assess_tmdb_tv_watch_providers_v1(
        self,
        *,
        series_id: int,
        country: str | None,
        api_key: str,
        client: httpx.AsyncClient,
    ) -> Awaitable[AvailabilityAssessmentsResponseV1]:
        ...
