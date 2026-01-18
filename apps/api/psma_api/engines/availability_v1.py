from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

from psma_api.models.availability import AvailabilityAssessmentV1, AvailabilityAssessmentsResponseV1
from psma_api.service_registry import ServiceCategory, tmdb_provider_id_to_service


@dataclass(frozen=True)
class TmdbOffering:
    provider_id: int
    provider_name: str | None
    monetization_types: tuple[str, ...]


def _iso_country(country: str | None) -> str:
    return (country or "US").upper()


def _infer_category_from_monetization(monetization_types: set[str]) -> ServiceCategory:
    if "flatrate" in monetization_types or "subscription" in monetization_types:
        return "svod"
    if "free" in monetization_types or "ads" in monetization_types:
        return "avod"
    if "rent" in monetization_types or "buy" in monetization_types:
        return "tvod"
    return "unknown"


def _extract_tmdb_offerings(region_result: Any) -> list[TmdbOffering]:
    if not isinstance(region_result, dict):
        return []

    buckets = ["flatrate", "free", "ads", "rent", "buy"]
    by_provider: dict[int, dict[str, Any]] = {}

    for bucket in buckets:
        items = region_result.get(bucket)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            provider_id = item.get("provider_id")
            provider_name = item.get("provider_name")
            if not isinstance(provider_id, int):
                continue
            if provider_id not in by_provider:
                by_provider[provider_id] = {
                    "provider_name": provider_name if isinstance(provider_name, str) else None,
                    "monetization": set(),
                }
            by_provider[provider_id]["monetization"].add(bucket)

    offerings: list[TmdbOffering] = []
    for provider_id, data in by_provider.items():
        monetization_types = tuple(sorted(data["monetization"]))
        offerings.append(
            TmdbOffering(
                provider_id=provider_id,
                provider_name=data.get("provider_name"),
                monetization_types=monetization_types,
            )
        )

    return offerings


async def assess_tmdb_tv_watch_providers_v1(
    *,
    series_id: int,
    country: str | None,
    api_key: str,
    client: httpx.AsyncClient,
) -> AvailabilityAssessmentsResponseV1:
    """Assess best-effort on-demand availability for a TMDB TV series.

    This uses TMDB's watch-provider snapshot API. It does not attempt to infer
    true start/end windows beyond "available now".
    """

    region = _iso_country(country)
    url = f"https://api.themoviedb.org/3/tv/{series_id}/watch/providers"

    resp = await client.get(url, params={"api_key": api_key})
    resp.raise_for_status()
    payload: Any = resp.json()

    results: Any = payload.get("results") if isinstance(payload, dict) else None
    region_result: Any = results.get(region) if isinstance(results, dict) else None

    offerings = _extract_tmdb_offerings(region_result)
    mapping = tmdb_provider_id_to_service()

    now = datetime.now(timezone.utc)
    title_id = f"tmdb:tv:{series_id}"

    assessments: list[AvailabilityAssessmentV1] = []
    for off in offerings:
        reason_codes: list[str] = ["TMDB_WATCH_PROVIDER_PRESENT"]

        entry = mapping.get(off.provider_id)
        if entry is not None:
            service_id = entry.service_id
            provider_category: ServiceCategory = entry.category
            reason_codes.append("SERVICE_ID_MAPPED")
        else:
            service_id = f"unknown-tmdb-provider-{off.provider_id}"
            provider_category = _infer_category_from_monetization(set(off.monetization_types))
            reason_codes.append("SERVICE_ID_UNKNOWN")
            if provider_category != "unknown":
                reason_codes.append("CATEGORY_INFERRED")

        details: dict[str, Any] = {
            "tmdb_series_id": series_id,
            "tmdb_provider_id": off.provider_id,
            "tmdb_provider_name": off.provider_name,
            "monetization_types": list(off.monetization_types),
        }

        assessments.append(
            AvailabilityAssessmentV1(
                title_id=title_id,
                country=region,
                service_id=service_id,
                provider_category=provider_category,  # type: ignore[arg-type]
                availability_now="true",
                confidence="medium",
                reason_codes=reason_codes,
                evidence=[
                    {
                        "source_id": "tmdb_watch_providers",
                        "retrieved_at": now,
                        "source_ref": f"tmdb:/tv/{series_id}/watch/providers",
                        "details": details,
                    }
                ],
            )
        )

    return AvailabilityAssessmentsResponseV1(retrieved_at=now, assessments=assessments)
