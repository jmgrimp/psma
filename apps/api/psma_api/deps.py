from __future__ import annotations

from collections.abc import AsyncIterator
import logging
import time

import httpx
from fastapi import Request

from psma_api.engines.availability_engine_impl import DefaultAvailabilityEngine
from psma_api.engines.planner_engine_impl import DefaultPlannerEngine
from psma_api.ports.availability_engine import AvailabilityEngine
from psma_api.ports.planner_engine import PlannerEngine

from psma_api.settings import settings


logger = logging.getLogger("psma_api.http")


def _safe_url(url: httpx.URL) -> str:
    # Avoid logging query params (TMDB api_key is in the query)
    return str(url.copy_with(query=None))


async def _on_request(request: httpx.Request) -> None:
    request.extensions["psma_start"] = time.perf_counter()
    logger.debug(
        "upstream_request",
        extra={
            "upstream": request.url.host,
            "method": request.method,
            "path": request.url.path,
            "url": _safe_url(request.url),
        },
    )


async def _on_response(response: httpx.Response) -> None:
    start = response.request.extensions.get("psma_start")
    duration_ms = None
    if isinstance(start, (int, float)):
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

    logger.debug(
        "upstream_response",
        extra={
            "upstream": response.request.url.host,
            "method": response.request.method,
            "path": response.request.url.path,
            "url": _safe_url(response.request.url),
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )


def build_http_client(*, transport: httpx.AsyncBaseTransport | None = None) -> httpx.AsyncClient:
    timeout = httpx.Timeout(settings.http_timeout_seconds)
    limits = httpx.Limits(
        max_keepalive_connections=20,
        max_connections=100,
        keepalive_expiry=30.0,
    )

    if transport is None:
        transport = httpx.AsyncHTTPTransport(retries=2)

    return httpx.AsyncClient(
        timeout=timeout,
        limits=limits,
        headers={
            "User-Agent": settings.user_agent,
            "Accept": "application/json",
        },
        transport=transport,
        follow_redirects=True,
        event_hooks={"request": [_on_request], "response": [_on_response]},
    )


async def get_http_client(request: Request) -> AsyncIterator[httpx.AsyncClient]:
    existing = getattr(request.app.state, "http_client", None)
    if isinstance(existing, httpx.AsyncClient):
        yield existing
        return

    async with build_http_client() as client:
        yield client


def get_availability_engine() -> AvailabilityEngine:
    # Kept intentionally simple for MVP. In the future, this can be swapped via:
    # - configuration (import path)
    # - entrypoints/plugin discovery
    # - a worker process using the same contract
    return DefaultAvailabilityEngine()


def get_planner_engine() -> PlannerEngine:
    # Kept intentionally simple for MVP. In the future, this can be swapped via:
    # - configuration (import path)
    # - entrypoints/plugin discovery
    # - a worker process using the same contract
    return DefaultPlannerEngine()
