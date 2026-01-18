from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
import json

import httpx
from fastapi.testclient import TestClient
from jsonschema import validate

from psma_api.deps import get_http_client
from psma_api.main import app
from psma_api.settings import settings


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_schema(rel_path: str) -> dict:
    return json.loads((_repo_root() / rel_path).read_text(encoding="utf-8"))


def test_availability_v1_facade_is_schema_valid() -> None:
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
                        "flatrate": [
                            {"provider_id": 8, "provider_name": "Netflix"},
                        ]
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
            "/availability/v1/tmdb/tv/1396",
            params={"country": "US"},
        )
        assert resp.status_code == 200
        body = resp.json()

        assessment_schema = _load_schema(
            "contracts/jsonschema/availability/availability-assessment.v1.schema.json"
        )
        response_schema = _load_schema(
            "contracts/jsonschema/availability/availability-assessments-response.v1.schema.json"
        )

        combined_schema = dict(response_schema)
        combined_schema["properties"] = dict(response_schema.get("properties", {}))
        combined_schema["properties"]["assessments"] = dict(
            combined_schema["properties"].get("assessments", {})
        )
        combined_schema["properties"]["assessments"]["items"] = assessment_schema

        validate(instance=body, schema=combined_schema)
        assert any(a["service_id"] == "netflix" for a in body["assessments"])
    finally:
        app.dependency_overrides.clear()
        settings.tmdb_api_key = prior
