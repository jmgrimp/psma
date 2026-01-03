from __future__ import annotations

from typing import Any, Literal

import httpx
from fastapi import APIRouter, Depends, HTTPException

from psma_api.deps import get_http_client
from psma_api.models.providers import Attribution, ProviderEnvelope

router = APIRouter(prefix="/providers/tvmaze", tags=["providers"])

TVMAZE_BASE_URL = "https://api.tvmaze.com"

TVMAZE_ATTRIBUTION = Attribution(
    required=True,
    text="Data from TVmaze (licensed CC BY-SA 4.0). Ensure attribution + ShareAlike compliance.",
    url="https://www.tvmaze.com/api",
)

AllowedEmbed = Literal[
    "cast",
    "crew",
    "episodes",
    "seasons",
    "akas",
    "images",
    "nextepisode",
    "previousepisode",
]


@router.get("/search/shows", response_model=ProviderEnvelope)
async def tvmaze_search_shows(
    q: str,
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ProviderEnvelope:
    url = f"{TVMAZE_BASE_URL}/search/shows"
    try:
        resp = await client.get(url, params={"q": q})
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "TVmaze returned an error",
                "upstream_status": exc.response.status_code,
                "upstream_body": exc.response.text,
            },
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail={"message": "TVmaze request failed", "error": str(exc)},
        ) from exc

    data: Any = resp.json()
    return ProviderEnvelope(
        provider="tvmaze",
        attribution=TVMAZE_ATTRIBUTION,
        request={"q": q, "url": url},
        data=data,
    )


@router.get("/shows/{show_id}", response_model=ProviderEnvelope)
async def tvmaze_get_show(
    show_id: int,
    embed: AllowedEmbed | None = None,
    client: httpx.AsyncClient = Depends(get_http_client),
) -> ProviderEnvelope:
    url = f"{TVMAZE_BASE_URL}/shows/{show_id}"
    params: dict[str, str] = {}
    if embed is not None:
        params["embed"] = embed

    try:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "TVmaze returned an error",
                "upstream_status": exc.response.status_code,
                "upstream_body": exc.response.text,
            },
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail={"message": "TVmaze request failed", "error": str(exc)},
        ) from exc

    data: Any = resp.json()
    return ProviderEnvelope(
        provider="tvmaze",
        attribution=TVMAZE_ATTRIBUTION,
        request={"show_id": show_id, "embed": embed, "url": url},
        data=data,
    )
