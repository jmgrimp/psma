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
    # apps/api/tests/... -> repo root is 3 parents up from apps/api
    return Path(__file__).resolve().parents[3]


def _load_schema(rel_path: str) -> dict:
    return json.loads((_repo_root() / rel_path).read_text(encoding="utf-8"))


def test_availability_engine_tmdb_tv_assessments_schema_valid() -> None:
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
                        "flatrate": [
                            {"provider_id": 8, "provider_name": "Netflix"},
                            {"provider_id": 350, "provider_name": "Apple TV+"},
                        ],
                        "free": [{"provider_id": 999, "provider_name": "Some Free App"}],
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
            "/engines/availability/v1/tmdb/tv/1396/assessments",
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

        # Inline the $ref so jsonschema can validate without external resolution.
        combined_schema = dict(response_schema)
        combined_schema["properties"] = dict(response_schema.get("properties", {}))
        combined_schema["properties"]["assessments"] = dict(
            combined_schema["properties"].get("assessments", {})
        )
        combined_schema["properties"]["assessments"]["items"] = assessment_schema

        assert set(body.keys()) == {"retrieved_at", "assessments"}
        validate(instance=body, schema=combined_schema)

        assert isinstance(body["assessments"], list)
        assert len(body["assessments"]) == 3
        for item in body["assessments"]:
            validate(instance=item, schema=assessment_schema)

        # Registry-mapped services should use canonical service_id.
        service_ids = {a["service_id"] for a in body["assessments"]}
        assert "netflix" in service_ids
        assert "apple-tv-plus" in service_ids

        # Unknown provider ids should still be stable and schema-valid.
        assert any(s.startswith("unknown-tmdb-provider-") for s in service_ids)

    finally:
        app.dependency_overrides.clear()
        settings.tmdb_api_key = prior
