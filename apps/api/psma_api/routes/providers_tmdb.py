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


def _normalize_watch_region(country: str | None) -> str:
    # TMDB uses watch_region. We keep a PSMA-friendly `country` parameter.
    return (country or "US").upper()


def _monetization_types_param(monetization_types: str | None) -> str | None:
    if not monetization_types:
        return None
    parts = [p.strip() for p in monetization_types.split(",") if p.strip()]
    if not parts:
        return None
    return "|".join(parts)


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


@router.get("/watch/providers/tv", response_model=ProviderEnvelope)
async def tmdb_watch_providers_tv(
    country: str | None = None,
    language: str | None = None,
    api_key: str = Depends(require_tmdb_key),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ProviderEnvelope:
    """List streaming providers for TV in a region.

    UI can call this to populate a provider selector. The returned items include
    TMDB provider ids needed for discovery.
    """

    url = f"{TMDB_BASE_URL}/watch/providers/tv"
    params: dict[str, Any] = {
        "api_key": api_key,
        "watch_region": _normalize_watch_region(country),
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
        request={"country": country, "language": language, "url": url},
        data=data,
    )


@router.get("/discover/tv", response_model=ProviderEnvelope)
async def tmdb_discover_tv_by_provider(
    watch_provider_id: int,
    country: str | None = None,
    monetization_types: str | None = "flatrate",
    language: str | None = None,
    sort_by: str | None = None,
    page: int | None = None,
    api_key: str = Depends(require_tmdb_key),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ProviderEnvelope:
    """Discover TV shows available on a selected provider.

    Example: Netflix in US
    - watch_provider_id=8
    - country=US
    - monetization_types=flatrate

    `monetization_types` is a comma-separated list (e.g. "flatrate,free,ads").
    """

    url = f"{TMDB_BASE_URL}/discover/tv"
    params: dict[str, Any] = {
        "api_key": api_key,
        "watch_region": _normalize_watch_region(country),
        "with_watch_providers": str(watch_provider_id),
    }

    monetization = _monetization_types_param(monetization_types)
    if monetization:
        params["with_watch_monetization_types"] = monetization

    if language:
        params["language"] = language
    if sort_by:
        params["sort_by"] = sort_by
    if page is not None:
        params["page"] = page

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
        # Discovery results are based on watch-provider availability; keep attribution aligned.
        attribution=TMDB_ATTRIBUTION,
        request={
            "watch_provider_id": watch_provider_id,
            "country": country,
            "monetization_types": monetization_types,
            "language": language,
            "sort_by": sort_by,
            "page": page,
            "url": url,
        },
        data=data,
    )


@router.get("/genre/tv/list", response_model=ProviderEnvelope)
async def tmdb_tv_genre_list(
    language: str | None = None,
    api_key: str = Depends(require_tmdb_key),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ProviderEnvelope:
    """List TV genres.

    UI can call this to populate a genre selector.
    """

    url = f"{TMDB_BASE_URL}/genre/tv/list"
    params: dict[str, Any] = {"api_key": api_key}
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
        request={"language": language, "url": url},
        data=data,
    )


@router.get("/discover/tv/by-genre", response_model=ProviderEnvelope)
async def tmdb_discover_tv_by_genre(
    genre_id: int,
    language: str | None = None,
    sort_by: str | None = None,
    page: int | None = None,
    api_key: str = Depends(require_tmdb_key),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ProviderEnvelope:
    """Discover TV shows for a given TMDB genre.

    Note: TMDB discovery is paginated (typically 20 per page). For now we expose
    a single page.
    """

    url = f"{TMDB_BASE_URL}/discover/tv"
    params: dict[str, Any] = {
        "api_key": api_key,
        "with_genres": str(genre_id),
    }
    if language:
        params["language"] = language
    if sort_by:
        params["sort_by"] = sort_by
    if page is not None:
        params["page"] = page

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
        request={"genre_id": genre_id, "language": language, "sort_by": sort_by, "page": page, "url": url},
        data=data,
    )
