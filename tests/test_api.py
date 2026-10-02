import threading
import time

import pytest
from fastapi.testclient import TestClient

from recruitment_assistant import api

VALID_REPORT = """\
## Advisory
Recruiter review is required. No hiring decision or message was made.

## Ranked Recommendations
Candidate A: 85/100. Strong Python service evidence.

## Evidence and Uncertainty
Synthetic fixture. Contact: unknown - verify.

## Outreach Drafts
Draft only; no message was sent.
"""


@pytest.fixture(autouse=True)
def reset_registry():
    api.registry.reset_for_tests()
    yield
    api.registry.reset_for_tests()


@pytest.fixture
def client():
    with TestClient(api.app) as test_client:
        yield test_client


def wait_for_terminal_status(client: TestClient, run_id: str) -> dict:
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        response = client.get(f"/api/runs/{run_id}")
        assert response.status_code == 200
        payload = response.json()
        if payload["status"] in {"succeeded", "failed"}:
            return payload
        time.sleep(0.01)
    pytest.fail("Run did not reach a terminal state.")


def test_health_endpoint(client: TestClient):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_blank_job_requirements_are_rejected(client: TestClient):
    response = client.post("/api/runs", json={"job_requirements": "  "})

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "validation_error"


def test_unknown_run_returns_not_found(client: TestClient):
    response = client.get("/api/runs/not-a-run")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "run_not_found"


def test_terminal_run_expires_after_idle_ttl(monkeypatch):
    registry = api.RunRegistry()
    monkeypatch.setattr(api, "RUN_TTL_SECONDS", 0)
    run = registry.reserve()
    registry.complete(run.run_id, VALID_REPORT)
    registry.release(run.run_id)
    registry._runs[run.run_id].last_access_at -= 1

    assert registry.get(run.run_id) is None


def test_run_returns_report_after_background_execution(client: TestClient, monkeypatch):
    monkeypatch.setattr(api, "run_crew", lambda _requirements, _profiles: VALID_REPORT)

    accepted = client.post("/api/runs", json={"job_requirements": "Python backend engineer"})

    assert accepted.status_code == 202
    assert accepted.json()["status"] == "queued"
    result = wait_for_terminal_status(client, accepted.json()["run_id"])
    assert result["status"] == "succeeded"
    assert result["report_markdown"] == VALID_REPORT


def test_concurrent_run_is_rejected(client: TestClient, monkeypatch):
    started = threading.Event()
    release = threading.Event()

    def blocked_crew(_requirements, _profiles):
        started.set()
        release.wait(timeout=3)
        return VALID_REPORT

    monkeypatch.setattr(api, "run_crew", blocked_crew)
    try:
        accepted = client.post("/api/runs", json={"job_requirements": "Python engineer"})
        assert accepted.status_code == 202
        assert started.wait(timeout=1)

        rejected = client.post("/api/runs", json={"job_requirements": "Another role"})
        assert rejected.status_code == 429
        assert rejected.json()["error"]["code"] == "run_busy"
    finally:
        release.set()


def test_failure_response_does_not_expose_exception_content(client: TestClient, monkeypatch):
    def failed_crew(_requirements, _profiles):
        raise RuntimeError("OPENAI_API_KEY=not-for-clients")

    monkeypatch.setattr(api, "run_crew", failed_crew)
    accepted = client.post("/api/runs", json={"job_requirements": "Python engineer"})
    result = wait_for_terminal_status(client, accepted.json()["run_id"])

    assert result["status"] == "failed"
    assert result["error"]["code"] == "crew_failed"
    assert "not-for-clients" not in str(result)