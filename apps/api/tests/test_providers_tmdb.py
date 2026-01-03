from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
from fastapi.testclient import TestClient

from psma_api.deps import get_http_client
from psma_api.main import app
from psma_api.settings import settings


def test_tmdb_requires_api_key() -> None:
    prior = settings.tmdb_api_key
    settings.tmdb_api_key = None
    try:
        client = TestClient(app)
        resp = client.get("/providers/tmdb/search/tv", params={"query": "Breaking Bad"})
        assert resp.status_code == 503
        body = resp.json()
        assert body["detail"]["message"] == "TMDB API key not configured"
    finally:
        settings.tmdb_api_key = prior


def test_tmdb_search_tv() -> None:
    prior = settings.tmdb_api_key
    settings.tmdb_api_key = "test-key"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "api.themoviedb.org"
        assert request.url.path == "/3/search/tv"
        assert request.url.params.get("api_key") == "test-key"
        assert request.url.params.get("query") == "Breaking Bad"
        return httpx.Response(
            200,
            json={"page": 1, "results": [{"id": 1396, "name": "Breaking Bad"}]},
        )

    transport = httpx.MockTransport(handler)

    async def override_client() -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient(transport=transport) as client:
            yield client

    app.dependency_overrides[get_http_client] = override_client
    try:
        client = TestClient(app)
        resp = client.get("/providers/tmdb/search/tv", params={"query": "Breaking Bad"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["provider"] == "tmdb"
        assert body["data"]["results"][0]["id"] == 1396
    finally:
        app.dependency_overrides.clear()
        settings.tmdb_api_key = prior


def test_tmdb_watch_providers_country_filter() -> None:
    prior = settings.tmdb_api_key
    settings.tmdb_api_key = "test-key"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "api.themoviedb.org"
        assert request.url.path == "/3/tv/1396/watch/providers"
        assert request.url.params.get("api_key") == "test-key"
        return httpx.Response(
            200,
            json={
                "id": 1396,
                "results": {
                    "US": {
                        "link": "https://www.themoviedb.org/tv/1396-breaking-bad/watch",
                        "flatrate": [{"provider_id": 8, "provider_name": "Netflix"}],
                    }
                },
            },
        )

    transport = httpx.MockTransport(handler)

    async def override_client() -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient(transport=transport) as client:
            yield client

    app.dependency_overrides[get_http_client] = override_client
    try:
        client = TestClient(app)
        resp = client.get(
            "/providers/tmdb/tv/1396/watch/providers",
            params={"country": "US"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["provider"] == "tmdb"
        assert body["data"]["id"] == 1396
        assert body["data"]["country"] == "US"
        assert body["data"]["result"]["flatrate"][0]["provider_name"] == "Netflix"
        assert body["attribution"]["required"] is True
    finally:
        app.dependency_overrides.clear()
        settings.tmdb_api_key = prior
