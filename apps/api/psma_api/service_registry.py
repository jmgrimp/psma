from __future__ import annotations

from dataclasses import dataclass
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal


ServiceCategory = Literal["svod", "avod", "tvod", "live_bundle", "unknown"]


@dataclass(frozen=True)
class ServiceRegistryEntry:
    service_id: str
    display_name: str
    category: ServiceCategory
    tmdb_watch_provider_ids: tuple[int, ...]


def _repo_root() -> Path:
    # apps/api/psma_api/service_registry.py -> repo root is 3 parents up from apps/api
    return Path(__file__).resolve().parents[3]


def _registry_path() -> Path:
    return _repo_root() / "contracts" / "registry" / "service-registry.v1.json"


@lru_cache(maxsize=1)
def load_service_registry() -> tuple[ServiceRegistryEntry, ...]:
    path = _registry_path()
    raw = json.loads(path.read_text(encoding="utf-8"))
    services = raw.get("services")
    if not isinstance(services, list):
        return tuple()

    entries: list[ServiceRegistryEntry] = []
    for item in services:
        if not isinstance(item, dict):
            continue
        service_id = item.get("service_id")
        display_name = item.get("display_name")
        category = item.get("category")
        external_ids: Any = item.get("external_ids")
        tmdb_ids: list[int] = []
        if isinstance(external_ids, dict):
            ids = external_ids.get("tmdb_watch_provider_id")
            if isinstance(ids, list):
                for v in ids:
                    if isinstance(v, int):
                        tmdb_ids.append(v)

        if not isinstance(service_id, str) or not service_id:
            continue
        if not isinstance(display_name, str) or not display_name:
            display_name = service_id
        if category not in {"svod", "avod", "tvod", "live_bundle", "unknown"}:
            category = "unknown"

        entries.append(
            ServiceRegistryEntry(
                service_id=service_id,
                display_name=display_name,
                category=category,  # type: ignore[arg-type]
                tmdb_watch_provider_ids=tuple(tmdb_ids),
            )
        )

    return tuple(entries)


@lru_cache(maxsize=1)
def tmdb_provider_id_to_service() -> dict[int, ServiceRegistryEntry]:
    mapping: dict[int, ServiceRegistryEntry] = {}
    for entry in load_service_registry():
        for pid in entry.tmdb_watch_provider_ids:
            mapping[pid] = entry
    return mapping
