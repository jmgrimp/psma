from __future__ import annotations

from pathlib import Path
import json
from datetime import datetime

from fastapi.testclient import TestClient
from jsonschema import validate

from psma_api.main import app


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_schema(rel_path: str) -> dict:
    return json.loads((_repo_root() / rel_path).read_text(encoding="utf-8"))


def _parse_dt(dt: str) -> datetime:
    # FastAPI returns RFC3339/ISO8601 with Z for UTC.
    if dt.endswith("Z"):
        dt = dt[:-1] + "+00:00"
    return datetime.fromisoformat(dt)


def test_planning_v1_generate_is_schema_valid_and_respects_permanent_services() -> None:
    client = TestClient(app)

    request_body = {
        "country": "US",
        "horizon_days": 30,
        "permanent_service_ids": ["youtube_tv"],
        "assessments": [
            {
                "title_id": "tmdb:tv:1396",
                "country": "US",
                "service_id": "netflix",
                "provider_category": "svod",
                "availability_now": "true",
                "confidence": "high",
                "reason_codes": ["tmdb_watch_provider_snapshot"],
                "evidence": [
                    {
                        "source_id": "tmdb",
                        "retrieved_at": "2026-01-01T00:00:00Z",
                        "details": {"provider_id": 8},
                    }
                ],
            },
            {
                "title_id": "tmdb:tv:1396",
                "country": "US",
                "service_id": "youtube_tv",
                "provider_category": "live_bundle",
                "availability_now": "true",
                "confidence": "medium",
                "reason_codes": ["tmdb_watch_provider_snapshot"],
                "evidence": [
                    {
                        "source_id": "tmdb",
                        "retrieved_at": "2026-01-01T00:00:00Z",
                        "details": {"provider_id": 1000},
                    }
                ],
            },
        ],
    }

    resp = client.post("/plan/v1/generate", json=request_body)
    assert resp.status_code == 200
    body = resp.json()

    response_schema = _load_schema("contracts/jsonschema/planning/plan-response.v1.schema.json")
    validate(instance=body, schema=response_schema)

    # Should include an event for netflix (not permanent)
    assert any(e["service_id"] == "netflix" and e["action"] == "subscribe" for e in body["events"])

    # Must NOT generate events for permanent services
    assert all(e["service_id"] != "youtube_tv" for e in body["events"])


def test_planning_v1_does_not_emit_events_for_unknown_services() -> None:
    client = TestClient(app)

    request_body = {
        "country": "US",
        "horizon_days": 30,
        "permanent_service_ids": [],
        "assessments": [
            {
                "title_id": "tmdb:tv:66732",
                "country": "US",
                "service_id": "unknown-tmdb-provider-1796",
                "provider_category": "unknown",
                "availability_now": "true",
                "confidence": "medium",
                "reason_codes": ["SERVICE_ID_UNKNOWN", "TMDB_WATCH_PROVIDER_PRESENT"],
                "evidence": [
                    {
                        "source_id": "tmdb_watch_providers",
                        "retrieved_at": "2026-01-01T00:00:00Z",
                        "details": {"tmdb_provider_id": 1796},
                    }
                ],
            }
        ],
    }

    resp = client.post("/plan/v1/generate", json=request_body)
    assert resp.status_code == 200
    body = resp.json()

    response_schema = _load_schema("contracts/jsonschema/planning/plan-response.v1.schema.json")
    validate(instance=body, schema=response_schema)

    assert body["events"] == []


def test_planning_v1_emits_questions_when_missing_unsubscribe_inputs() -> None:
    client = TestClient(app)

    request_body = {
        "country": "US",
        "horizon_days": 30,
        "permanent_service_ids": [],
        "assessments": [
            {
                "title_id": "tmdb:tv:66732",
                "country": "US",
                "service_id": "netflix",
                "provider_category": "svod",
                "availability_now": "true",
                "confidence": "high",
                "reason_codes": ["TMDB_WATCH_PROVIDER_PRESENT", "SERVICE_ID_MAPPED"],
                "evidence": [
                    {
                        "source_id": "tmdb_watch_providers",
                        "retrieved_at": "2026-01-01T00:00:00Z",
                        "details": {"tmdb_provider_id": 8},
                    }
                ],
            }
        ],
    }

    resp = client.post("/plan/v1/generate", json=request_body)
    assert resp.status_code == 200
    body = resp.json()

    response_schema = _load_schema("contracts/jsonschema/planning/plan-response.v1.schema.json")
    validate(instance=body, schema=response_schema)

    # Subscribe is still emitted for known services available now.
    assert any(e["service_id"] == "netflix" and e["action"] == "subscribe" for e in body["events"])

    # Planner should ask for missing inputs required to schedule an unsubscribe.
    qkeys = {q["key"] for q in body.get("questions", [])}
    assert "min_contract_days" in qkeys
    assert "estimated_watch_days" in qkeys


def test_planning_v1_emits_unsubscribe_when_inputs_present() -> None:
    client = TestClient(app)

    request_body = {
        "country": "US",
        "horizon_days": 60,
        "permanent_service_ids": [],
        "inputs": [
            {"key": "min_contract_days", "service_id": "netflix", "value": 30, "source_id": "test"},
            {"key": "estimated_watch_days", "service_id": "netflix", "value": 10, "source_id": "test"},
        ],
        "assessments": [
            {
                "title_id": "tmdb:tv:66732",
                "country": "US",
                "service_id": "netflix",
                "provider_category": "svod",
                "availability_now": "true",
                "confidence": "high",
                "reason_codes": ["TMDB_WATCH_PROVIDER_PRESENT", "SERVICE_ID_MAPPED"],
                "evidence": [
                    {
                        "source_id": "tmdb_watch_providers",
                        "retrieved_at": "2026-01-01T00:00:00Z",
                        "details": {"tmdb_provider_id": 8},
                    }
                ],
            }
        ],
    }

    resp = client.post("/plan/v1/generate", json=request_body)
    assert resp.status_code == 200
    body = resp.json()

    response_schema = _load_schema("contracts/jsonschema/planning/plan-response.v1.schema.json")
    validate(instance=body, schema=response_schema)

    netflix_events = [e for e in body["events"] if e["service_id"] == "netflix"]
    actions = {e["action"] for e in netflix_events}
    assert actions == {"subscribe", "unsubscribe"}

    sub = next(e for e in netflix_events if e["action"] == "subscribe")
    unsub = next(e for e in netflix_events if e["action"] == "unsubscribe")
    assert _parse_dt(unsub["effective_at"]) > _parse_dt(sub["effective_at"])

    # Inputs are sufficient; questions should be omitted (or empty).
    assert body.get("questions") in (None, [])
