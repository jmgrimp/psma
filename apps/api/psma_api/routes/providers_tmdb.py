from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException

from psma_api.deps import get_http_client
from psma_api.models.providers import Attribution, ProviderEnvelope
from psma_api.settings import settings

router = APIRouter(prefix="/providers/tmdb", tags=["providers"])

TMDB_BASE_URL = "https://api.themoviedb.org/3"

TMDB_ATTRIBUTION = Attribution(
    required=True,
    text="Watch provider data requires attribution to JustWatch per TMDB docs.",
    url="https://developer.themoviedb.org/reference/tv-series-watch-providers",
)


def require_tmdb_key() -> str:
    if not settings.tmdb_api_key:
        raise HTTPException(
            status_code=503,
            detail={
                "message": "TMDB API key not configured",
                "hint": "Set PSMA_TMDB_API_KEY in apps/api/.env and restart the API.",
            },
        )
    return settings.tmdb_api_key


@router.get("/search/tv", response_model=ProviderEnvelope)
async def tmdb_search_tv(
    query: str,
    language: str | None = None,
    include_adult: bool = False,
    api_key: str = Depends(require_tmdb_key),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ProviderEnvelope:
    url = f"{TMDB_BASE_URL}/search/tv"
    params: dict[str, Any] = {
        "api_key": api_key,
        "query": query,
        "include_adult": include_adult,
    }
    if language:
        params["language"] = language

    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
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

    data: Any = resp.json()
    return ProviderEnvelope(
        provider="tmdb",
        attribution=None,
        request={
            "query": query,
            "language": language,
            "include_adult": include_adult,
            "url": url,
        },
        data=data,
    )


@router.get("/tv/{series_id}/watch/providers", response_model=ProviderEnvelope)
async def tmdb_tv_watch_providers(
    series_id: int,
    country: str | None = None,
    api_key: str = Depends(require_tmdb_key),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ProviderEnvelope:
    url = f"{TMDB_BASE_URL}/tv/{series_id}/watch/providers"
    params: dict[str, Any] = {"api_key": api_key}

    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
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

    payload: Any = resp.json()
    if country is not None and isinstance(payload, dict):
        results = payload.get("results")
        if isinstance(results, dict):
            payload = {
                "id": payload.get("id"),
                "country": country,
                "result": results.get(country),
            }

    return ProviderEnvelope(
        provider="tmdb",
        attribution=TMDB_ATTRIBUTION,
        request={"series_id": series_id, "country": country, "url": url},
        data=payload,
    )
