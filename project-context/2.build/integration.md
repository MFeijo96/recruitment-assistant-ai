# Frontend and Backend Integration

**Status:** MVP chat flow wired; offline API round-trip verified
**Runtime:** `crewai` (`AAMAD_TARGET_RUNTIME=crewai`)
**Inputs reviewed:** PRD, SAD, frontend build, and backend implementation
**Workflow:** `@integration.eng` / `*integrate-api`, `*verify-messageflow`, `*log-integration`

## Integration

- The recruiter form posts JSON to `POST /api/runs` with trimmed `job_requirements` and the optional free-text `candidate_profiles` (empty by default).
- The API returns `202` with a run ID. The client polls `GET /api/runs/{run_id}` every second until `succeeded` or `failed`, with a client-side 490-second ceiling for the backend's 480-second run limit.
- On success the report is displayed as text in a `<pre>` element. React escapes the text; no raw HTML or remote markdown embeds are enabled.
- On failed HTTP requests or failed runs, the UI shows the API's sanitized message. While queued/running, the submit action is disabled and the report area reflects the current state.
- The “New shortlist” action aborts the browser request/polling and clears the UI. It does not forcibly cancel an already-running CrewAI worker; the backend continues to enforce its one-run gate until the worker returns.
- Vite proxies `/api` and `/healthz` to `http://127.0.0.1:8000`, keeping local browser traffic same-origin. The FastAPI CORS default allowlist is `http://localhost:5173`; use `FRONTEND_ORIGIN` for any direct cross-origin deployment. The development proxy is not a production reverse proxy.

## Verification

- The backend round-trip test stubs `run_crew`, posts a kickoff, polls the returned run ID, and verifies the successful report payload without contacting an LLM or search provider (`tests/test_api.py`: 7 passed).
- Full backend verification: `python -m pytest -q` (13 passed).
- VS Code diagnostics reported no errors in `App.tsx`, `api.ts`, or `vite.config.ts`.
- Frontend dependency installation/build and browser verification could not be run in this environment because Node.js and npm are unavailable.
- No live-provider CrewAI run was performed; the API round-trip check is intentionally deterministic and offline.

## Known Issues and Constraints

- Local end-to-end use requires the FastAPI service on `127.0.0.1:8000` and Vite on `127.0.0.1:5173`. Configure `OPENAI_API_KEY` in the backend environment for a real run; offline tests stub the crew.
- The integration scope is one active, in-memory run. Results disappear on backend restart and are subject to the backend's 15-minute idle expiry.
- Browser-side abort stops further polling but cannot stop the synchronous CrewAI call in its worker thread. A timed-out worker can continue occupying the backend's run slot until it returns, as documented in `backend.md`.
- This renderer preserves the report as plain text rather than formatting markdown. It is safe from HTML injection, but markdown headings and emphasis are shown literally.
- `project-context/2.build/setup.md` is absent; no setup artifact was available to review.
- The client polls status only; task-level progress, report download, persistent history, and production deployment support remain out of scope.

## Run Locally

Start the backend from the repository root:

```powershell
python -m uvicorn recruitment_assistant.api:app --app-dir src --host 127.0.0.1 --port 8000
```

Start the frontend from `frontend/`:

```powershell
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. For a real CrewAI run, provide `OPENAI_API_KEY` to the backend process. Fixture-backed API tests do not require provider credentials.

## Sources

- `project-context/1.define/prd.md` — MVP API inputs, report behavior, safe sourcing, and acceptance criteria.
- `project-context/1.define/sad.md` — asynchronous kickoff/status API, frontend/backend boundary, and data handling.
- `project-context/2.build/frontend.md` — implemented UI and local frontend origin.
- `project-context/2.build/backend.md` — FastAPI routes, run limits, error handling, and known worker cancellation constraint.
- `.cursor/agents/integration-eng.md` — integration scope, validation, and documentation requirements.

## Assumptions

- Local development uses the Vite proxy and a backend listening at `127.0.0.1:8000`; a separate deployment must configure its own same-origin proxy or `FRONTEND_ORIGIN` CORS setting.
- The first environment uses synthetic or fixture profiles only. A live model call is optional and was not required for offline API verification.
- Rendering the markdown source as escaped plain text is acceptable for this MVP; formatted markdown rendering is deferred.

## Open Questions

- No API contract decisions remain open. Frontend build and browser smoke verification remain pending until Node.js/npm are available.

## Audit

- **Resolved runtime:** `AAMAD_TARGET_RUNTIME=crewai`.
- **API contract:** SAD `/api/runs` asynchronous kickoff, run status polling, `report_markdown` success, sanitized `error` failure.
- **Data handling:** request/report held in component memory and backend process memory only; no browser persistence added.
- **Sourcing policy:** integration adds no external service or sourcing tools; fixture/synthetic data policy remains in force.
- **Timestamp:** 2026-10-02.