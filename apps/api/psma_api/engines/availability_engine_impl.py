from __future__ import annotations

import httpx

from psma_api.engines.availability_v1 import assess_tmdb_tv_watch_providers_v1
from psma_api.models.availability import AvailabilityAssessmentsResponseV1


class DefaultAvailabilityEngine:
    async def assess_tmdb_tv_watch_providers_v1(
        self,
        *,
        series_id: int,
        country: str | None,
        api_key: str,
        client: httpx.AsyncClient,
    ) -> AvailabilityAssessmentsResponseV1:
        return await assess_tmdb_tv_watch_providers_v1(
            series_id=series_id,
            country=country,
            api_key=api_key,
            client=client,
        )
