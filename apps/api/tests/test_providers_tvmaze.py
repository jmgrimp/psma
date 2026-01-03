from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
from fastapi.testclient import TestClient

from psma_api.deps import get_http_client
from psma_api.main import app


def test_tvmaze_search_shows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "api.tvmaze.com"
        assert request.url.path == "/search/shows"
        assert request.url.params.get("q") == "girls"
        return httpx.Response(
            200,
            json=[
                {
                    "score": 1.0,
                    "show": {"id": 1, "name": "Girls"},
                }
            ],
        )

    transport = httpx.MockTransport(handler)

    async def override_client() -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient(transport=transport) as client:
            yield client

    app.dependency_overrides[get_http_client] = override_client
    try:
        client = TestClient(app)
        resp = client.get("/providers/tvmaze/search/shows", params={"q": "girls"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["provider"] == "tvmaze"
        assert isinstance(body["data"], list)
        assert body["data"][0]["show"]["name"] == "Girls"
        assert body["attribution"]["required"] is True
    finally:
        app.dependency_overrides.clear()


def test_tvmaze_get_show_with_embed() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "api.tvmaze.com"
        assert request.url.path == "/shows/1"
        assert request.url.params.get("embed") == "episodes"
        return httpx.Response(
            200,
            json={"id": 1, "name": "Girls", "_embedded": {"episodes": []}},
        )

    transport = httpx.MockTransport(handler)

    async def override_client() -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient(transport=transport) as client:
            yield client

    app.dependency_overrides[get_http_client] = override_client
    try:
        client = TestClient(app)
        resp = client.get("/providers/tvmaze/shows/1", params={"embed": "episodes"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["provider"] == "tvmaze"
        assert body["data"]["_embedded"]["episodes"] == []
    finally:
        app.dependency_overrides.clear()
