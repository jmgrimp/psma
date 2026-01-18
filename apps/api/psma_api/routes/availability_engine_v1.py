from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException

from psma_api.deps import get_http_client
from psma_api.engines.availability_v1 import assess_tmdb_tv_watch_providers_v1
from psma_api.models.availability import AvailabilityAssessmentsResponseV1
from psma_api.routes.providers_tmdb import require_tmdb_key


router = APIRouter(prefix="/engines/availability/v1", tags=["engines"])


@router.get(
    "/tmdb/tv/{series_id}/assessments",
    response_model=AvailabilityAssessmentsResponseV1,
    response_model_exclude_none=True,
)
async def assess_tmdb_tv(
    series_id: int,
    country: str | None = None,
    api_key: str = Depends(require_tmdb_key),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> Any:
    try:
        return await assess_tmdb_tv_watch_providers_v1(
            series_id=series_id,
            country=country,
            api_key=api_key,
            client=client,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "TMDB returned an error",
                "upstream_status": exc.response.status_code,
                "upstream_body": exc.response.text,
            },
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail={"message": "TMDB request failed", "error": str(exc)},
        ) from exc
