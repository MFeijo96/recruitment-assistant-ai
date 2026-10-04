# Deployment Runbook: Recruitment Assistant

## Release Scope

- **Release:** `0.1.0` (matches `pyproject.toml` and the frontend package version).
- **Runtime:** CrewAI, selected by `AAMAD_TARGET_RUNTIME=crewai`.
- **Included:** single-user recruiter UI, FastAPI run/status/health API, and three sequential CrewAI roles (Researcher, Evaluator, Recommender); fixture/synthetic profiles; optional gated Serper search; advisory markdown shortlist.
- **Excluded:** public production hiring, authentication/SSO, persistence, ATS integration, automated hiring decisions, and outbound candidate communication.
- **Release decision:** suitable only for local use or a controlled internal demo with synthetic/fixture data. Backend/API offline tests pass (13 total). Browser acceptance and a live provider-backed run remain unverified per [qa.md](../2.build/qa.md).
- **Security assessment:** `project-context/2.build/security.md` is absent. This is recorded as an accepted gap for this Tier-0 mini-project, not as a completed security review. Do not expose this release to a network or use real candidate data.

## Hosting

### Local

Run the API and Vite development UI as separate processes. The API listens on `127.0.0.1:8000`; the UI listens on `127.0.0.1:5173` and proxies `/api` and `/healthz` to the API.

### Docker-assisted local demo

Docker Compose builds and runs only the single-worker API container, bound to host loopback at `127.0.0.1:8000`. Run the Vite UI natively on the host as described in the local startup steps; its existing proxy targets host loopback and is not a production reverse proxy. This setup is not approved for public or shared-network hosting. No cloud resources are provisioned by this release.

## Environment Variables

Use only the keys already listed in the root `.env.example`. Copy it to `.env` for local or Compose use, then provide operator-owned values without committing `.env`.

| Key | Requirement / default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | Required for an actual CrewAI run | Provider credential; supply outside version control. |
| `OPENAI_MODEL` | Optional; `gpt-4o` | LLM model selection. |
| `SERPER_API_KEY` | Optional | Search credential; only used with web research explicitly enabled. |
| `AAMAD_ENABLE_WEB_RESEARCH` | Optional; `false` | Enables optional public search only when the Serper key is also present. Keep disabled for fixture-only demos. |
| `FRONTEND_ORIGIN` | Optional; `.env.example` uses `http://localhost:5173` | FastAPI CORS origin. Compose sets it to `http://127.0.0.1:5173` for the host UI. |
| `AAMAD_TARGET_RUNTIME` | Set to `crewai` | Runtime adapter selection. Compose and the image enforce this release target. |
| `APP_NAME` | Optional; `.env.example` default | Descriptive application setting; not used by current API logic. |
| `APP_ENV` | Optional; `.env.example` default | Descriptive environment setting; not used by current API logic. |
| `CREWAI_TELEMETRY_OPTOUT` | `.env.example` sets `true` | CrewAI telemetry preference. |
| `LOG_LEVEL` | Optional; `INFO` | Python application log threshold: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`. |
| `CREWAI_TRACING` | Optional; `false` | When `true`, the Application Crew is created with CrewAI's `tracing=True`; requires CrewAI account login. Tracing may include run inputs and outputs. |

No secret values belong in this document, Compose configuration, or source control. The Docker image does not copy `.env` into its build context.

## Install, Start, Stop, Roll Back

### Local install and start

Prerequisites: Python 3.11+, Node.js/npm, and an operator-provided `OPENAI_API_KEY` for live runs. From the repository root in PowerShell:

```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set the required provider value in the backend process environment (do not put it in a committed file). Start the API from the repository root:

```powershell
python main.py
```

In a second terminal:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The fixture fallback avoids external search when candidate profiles are omitted and web research is disabled, but CrewAI still requires a working LLM provider credential for a real run.

### Docker-assisted start

Install Docker Engine/Desktop with the Compose plugin, create `.env` from `.env.example`, and provide the required provider key in the local `.env`. From the repository root:

```powershell
docker compose up --build -d api
docker compose ps
```

Then install/start the Vite UI on the host using the local instructions above. Verify API liveness with `Invoke-RestMethod http://127.0.0.1:8000/healthz`.

### Stop

- Local: stop the API and Vite terminal processes with `Ctrl+C`.
- Docker: run `docker compose down` from the repository root. No volume or database needs cleanup; active runs and reports are process-memory-only and disappear when the API stops.

### Rollback

1. Stop the current service (`docker compose down`) or stop both local processes.
2. Restore the previously approved source revision/tag, preserving the operator's `.env` outside version control.
3. For Docker, rebuild and restart that revision with `docker compose up --build -d api`; for local use, reinstall its Python package if dependencies changed and restart the API/UI.
4. Check `/healthz`, then run the offline tests with `python -m pytest -q` before resuming demo use.

Rollback cannot restore in-flight runs or prior reports because they are intentionally non-persistent.

## Access Control

The MVP has no authentication or authorization. Both hosting instructions bind services to loopback for a single local operator. Do not change binds, publish ports through a proxy, or place the service on a shared/public network. Restrict provider keys to the required provider/project and rotate them through the provider if exposed. Use only bundled fixtures or synthetic candidate profiles; recruiter review is mandatory and the output must not be used as an automated hire/reject decision.

## Monitoring & Observability

### What to monitor

- `GET /healthz` is a process-liveness check only; it does not verify provider availability. Docker uses this endpoint for its container health check.
- Watch request status and duration, accepted/failed run counts, run duration, timeout/provider failures, and whether the API is returning `429` because a run is already active.
- Monitor provider availability and usage/cost in the provider account. There is no metrics backend, alerting, persistent trace store, or production APM in this release.

### Application logs

- Python application logs are written to standard output, not to files. Local runs print to the API terminal; inspect Docker output with `docker compose logs --tail 100 api` (or add `-f` to follow it).
- Set `LOG_LEVEL` to `DEBUG`, `INFO` (default), `WARNING`, `ERROR`, or `CRITICAL`. `INFO` includes application start/stop, HTTP method/path/status/duration, crew execution lifecycle, and run lifecycle. Failures are logged at `WARNING` or `ERROR` with sanitized error classes.
- Request paths are logged without query strings. Request/response bodies, prompts, candidate profiles, reports, credentials, and raw provider/tool error messages are not intentionally logged. Logs have no application-managed retention; retention depends on the terminal or container runtime.

### CrewAI tracing

Tracing is off by default. Setting `CREWAI_TRACING=true` passes `tracing=True` to the Application Crew. Authenticate the CrewAI CLI in the same local account/environment that runs the API, then enable the flag before starting the API:

```powershell
crewai login
$env:CREWAI_TRACING = "true"
python main.py
```

In the CrewAI dashboard, sign in with the account used by `crewai login`, select the corresponding workspace, and open its Tracing view to inspect crew executions. For Docker, CLI authentication must be available to the container process; do not bake login credentials into the image. Container credential persistence is not configured by this release.

CrewAI traces are separate from application logs and may capture task inputs, outputs, or other run details. Use synthetic/fixture data only when tracing is enabled; do not use traces with real candidate data or secrets. Turn tracing back off with `CREWAI_TRACING=false` when not needed.

## Troubleshooting

| Symptom | Checks / action |
| --- | --- |
| Compose reports `.env` missing | Copy `.env.example` to `.env` at the repository root. Keep actual credentials out of Git. |
| Container fails health check or port is occupied | Check `docker compose logs api`, ensure host port `8000` is free, then retry. The health endpoint checks API process liveness only. |
| UI cannot reach API | Ensure API is healthy on `127.0.0.1:8000` and Vite runs on `127.0.0.1:5173`; the Vite proxy is configured for those addresses. |
| Run fails with provider error | Confirm the backend process/container received `OPENAI_API_KEY`, `OPENAI_MODEL` is supported, and the provider is available. Inspect sanitized service logs; do not paste credentials into logs/issues. |
| Search does not run | Search is disabled by default. It requires both `SERPER_API_KEY` and `AAMAD_ENABLE_WEB_RESEARCH=true`; otherwise fixture behavior is expected. |
| Run reports busy or times out | Only one run may be active. The API caps run status at 480 seconds; a synchronous provider call may continue occupying its worker after timeout until it returns. Restarting clears process memory but interrupts any active run. |
| Previous report/run ID disappeared | Expected after API restart, 15 minutes without polling, or acceptance of a new run. Results are not backed up. |

## Sources

- `project-context/1.define/prd.md` — release requirements, scope, and human-review constraints.
- `project-context/1.define/sad.md` — service architecture, environment, deployment, and runtime limits.
- `project-context/2.build/qa.md` — backend test results and outstanding acceptance gaps.
- `project-context/2.build/backend.md`, `frontend.md`, and `integration.md` — implementation, local start commands, and integration constraints.
- `.cursor/agents/devops-eng.md`, `.cursor/rules/delivery-workflow.mdc`, and `.cursor/rules/adapter-crewai.mdc` — AAMAD delivery and CrewAI packaging requirements.
- `.env.example`, `pyproject.toml`, `Dockerfile`, and `docker-compose.yml` — environment names, package metadata, and container configuration.

## Assumptions

- The operator accepts the absent `security.md` assessment as a scoped Tier-0 gap for this local-only mini-project. `aamad.config.yml` still requires assessment; acceptance here does not satisfy or waive that project quality gate for future/shared/production use.
- QA's backend/API result (13 tests passing) is adequate for this limited local/demo release, while browser acceptance and a provider-backed run remain explicit gaps.
- Runtime is resolved as `AAMAD_TARGET_RUNTIME=crewai`; `pyproject.toml` and `requirements.txt` contain matching direct runtime dependencies. `main.py` starts the existing API module for local use.
- Docker hosts only the API; Vite runs on the host because the existing frontend proxy targets `127.0.0.1` and is development-only.
- Port `8000` and UI port `5173` are available on the local machine. The Docker image uses one Uvicorn worker because run state is process-local.
- The release is used with fixture/synthetic data only. No live cloud provisioning or deployment was performed.

## Open Questions

- Who will run and record frontend build/browser acceptance when Node.js/npm are available?
- Who will run and manually review a controlled provider-backed fixture workflow?
- Before any shared deployment, what authentication, network boundary, and formal security assessment are required? Until resolved, network exposure is not approved.

## Audit

- **Persona/action:** `devops-eng` / `prepare-release`, `define-deploy`, `document-deploy`.
- **Timestamp:** 2026-10-02.
- **Resolved runtime:** `AAMAD_TARGET_RUNTIME=crewai`.
- **Release version:** `0.1.0`.
- **QA gate:** backend offline checks pass (6 crew, 7 API, 13 combined); browser/provider end-to-end checks remain unverified as documented in `qa.md`.
- **Security status:** `project-context/2.build/security.md` absent; accepted scoped Tier-0 gap for local/demo only. Not a completed security assessment.
- **Packaging:** Python 3.11 image; API on one Uvicorn worker; Compose maps host loopback only. `pyproject.toml` remains dependency/package source of truth.
- **Verification limitations:** Docker and Node/npm executables are unavailable in the current environment; container build/health and browser build were not run. No production deployment or provider call was made.