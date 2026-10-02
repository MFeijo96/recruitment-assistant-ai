"""FastAPI application and ephemeral run-status API."""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from recruitment_assistant.crew import (
    CrewConfigurationError,
    ReportValidationError,
    run_crew,
)

logger = logging.getLogger("recruitment_assistant")
RUN_TTL_SECONDS = 15 * 60
MAX_EXECUTION_SECONDS = 480
WORKER = ThreadPoolExecutor(max_workers=1, thread_name_prefix="recruitment-crew")

RunStatus = Literal["queued", "running", "succeeded", "failed"]


class RunRequest(BaseModel):
    job_requirements: str
    candidate_profiles: str | None = ""


@dataclass
class RunRecord:
    run_id: str
    status: RunStatus
    created_at: float
    last_access_at: float
    report_markdown: str | None = None
    error: dict[str, str] | None = None


class RunRegistry:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._runs: dict[str, RunRecord] = {}
        self._active_run_id: str | None = None

    def _expire_idle_runs(self, now: float) -> None:
        expired = [
            run_id
            for run_id, run in self._runs.items()
            if run.status in ("succeeded", "failed")
            and now - run.last_access_at > RUN_TTL_SECONDS
        ]
        for run_id in expired:
            del self._runs[run_id]

    def reserve(self) -> RunRecord | None:
        now = time.monotonic()
        with self._lock:
            self._expire_idle_runs(now)
            if self._active_run_id is not None:
                return None
            self._runs.clear()
            run = RunRecord(
                run_id=str(uuid.uuid4()),
                status="queued",
                created_at=now,
                last_access_at=now,
            )
            self._runs[run.run_id] = run
            self._active_run_id = run.run_id
            return run

    def mark_running(self, run_id: str) -> None:
        with self._lock:
            run = self._runs.get(run_id)
            if run is not None and run.status == "queued":
                run.status = "running"

    def complete(self, run_id: str, report: str) -> None:
        with self._lock:
            run = self._runs.get(run_id)
            if run is not None and run.status in ("queued", "running"):
                run.status = "succeeded"
                run.report_markdown = report

    def fail(self, run_id: str, code: str, message: str) -> None:
        with self._lock:
            run = self._runs.get(run_id)
            if run is not None and run.status in ("queued", "running"):
                run.status = "failed"
                run.error = {"code": code, "message": message}

    def release(self, run_id: str) -> None:
        with self._lock:
            if self._active_run_id == run_id:
                self._active_run_id = None

    def get(self, run_id: str) -> RunRecord | None:
        now = time.monotonic()
        with self._lock:
            self._expire_idle_runs(now)
            run = self._runs.get(run_id)
            if run is not None:
                run.last_access_at = now
                return RunRecord(**vars(run))
            return None

    def reset_for_tests(self) -> None:
        with self._lock:
            self._runs.clear()
            self._active_run_id = None


registry = RunRegistry()
app = FastAPI(title="Recruitment Assistant API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def _execute_run(run_id: str, requirements: str, profiles: str) -> None:
    started_at = time.monotonic()
    registry.mark_running(run_id)
    logger.info("run_started run_id=%s", run_id)
    try:
        report = run_crew(requirements, profiles)
        registry.complete(run_id, report)
        logger.info("run_succeeded run_id=%s duration_seconds=%.2f", run_id, time.monotonic() - started_at)
    except CrewConfigurationError as error:
        registry.fail(run_id, "provider_failed", str(error))
        logger.warning("run_failed run_id=%s code=provider_failed", run_id)
    except (TimeoutError, asyncio.TimeoutError):
        registry.fail(run_id, "timeout", "The analysis exceeded the 480-second run limit.")
        logger.warning("run_failed run_id=%s code=timeout", run_id)
    except ReportValidationError:
        registry.fail(
            run_id,
            "crew_failed",
            "The crew returned a report that did not meet required safety and format checks.",
        )
        logger.warning("run_failed run_id=%s code=report_validation", run_id)
    except Exception as error:
        error_module = type(error).__module__.split(".", maxsplit=1)[0]
        error_name = type(error).__name__.lower()
        if error_module in {"openai", "litellm"} or "provider" in error_name:
            registry.fail(
                run_id,
                "provider_failed",
                "The language model provider could not complete the run. Check provider availability and credentials.",
            )
            logger.warning("run_failed run_id=%s code=provider_failed error_type=%s", run_id, type(error).__name__)
            return
        registry.fail(
            run_id,
            "crew_failed",
            "The crew could not complete this run. Check the backend configuration and try again.",
        )
        logger.error("run_failed run_id=%s code=crew_failed error_type=%s", run_id, type(error).__name__)
    finally:
        registry.release(run_id)


async def _watch_run(run_id: str, worker_future: asyncio.Future) -> None:
    try:
        await asyncio.wait_for(asyncio.shield(worker_future), timeout=MAX_EXECUTION_SECONDS)
    except asyncio.TimeoutError:
        registry.fail(run_id, "timeout", "The analysis exceeded the 480-second run limit.")
        logger.warning("run_failed run_id=%s code=timeout", run_id)
    except Exception as error:
        # _execute_run maps worker failures to sanitized run state.
        logger.error("run_worker_callback_failed run_id=%s error_type=%s", run_id, type(error).__name__)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/runs", status_code=202)
async def create_run(request: RunRequest) -> dict[str, str]:
    if not request.job_requirements.strip():
        raise HTTPException(
            status_code=400,
            detail={"error": {"code": "validation_error", "message": "job_requirements must not be blank."}},
        )

    run = registry.reserve()
    if run is None:
        raise HTTPException(
            status_code=429,
            detail={"error": {"code": "run_busy", "message": "Another recruitment run is already active."}},
        )

    loop = asyncio.get_running_loop()
    worker_future = loop.run_in_executor(
        WORKER,
        _execute_run,
        run.run_id,
        request.job_requirements.strip(),
        request.candidate_profiles or "",
    )
    asyncio.create_task(_watch_run(run.run_id, worker_future))
    return {"run_id": run.run_id, "status": "queued"}


@app.get("/api/runs/{run_id}")
async def get_run(run_id: str) -> dict:
    run = registry.get(run_id)
    if run is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "run_not_found", "message": "The run was not found or has expired."}},
        )

    response = {"run_id": run.run_id, "status": run.status}
    if run.status == "succeeded":
        response["report_markdown"] = run.report_markdown
    elif run.status == "failed":
        response["error"] = run.error
    return response


@app.exception_handler(HTTPException)
async def http_error_handler(_request: Request, exception: HTTPException) -> JSONResponse:
    detail = exception.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exception.status_code, content=detail)
    return JSONResponse(status_code=exception.status_code, content={"error": detail})


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    _request: Request, _exception: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": "The request body is invalid."}},
    )