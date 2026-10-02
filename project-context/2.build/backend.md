# Backend Implementation

**Status:** MVP backend implemented  
**Runtime:** `crewai` (`AAMAD_TARGET_RUNTIME=crewai`)  
**Architecture:** `project-context/1.define/sad.md`  
**Product requirements:** `project-context/1.define/prd.md`

## Implemented

- FastAPI exposes `POST /api/runs`, `GET /api/runs/{run_id}`, and `GET /healthz`.
- Kickoff validates non-blank job requirements, returns `202` with a run ID, and executes CrewAI on one bounded worker. A concurrent kickoff receives `429`.
- Run state and successful markdown reports are in memory only. Terminal results expire after 15 minutes without polling, a newly accepted run removes the prior result, and process restart clears state.
- The CrewAI crew is YAML-defined in `src/recruitment_assistant/config/agents.yaml` and `tasks.yaml`: Researcher, Evaluator, and Recommender run sequentially. Evaluator context includes research; Recommender context includes research and evaluation.
- Crew controls are `memory=False`, `max_rpm=10`, and sequential execution. Each agent has `allow_delegation=false`, `max_iter=8`, `max_retry_limit=2`, and CrewAI's supported 480-second execution limit; the API also marks the overall run failed at 480 seconds.
- LLM settings are `OPENAI_MODEL` (default `gpt-4o`), temperature `0`, and max tokens `2048`.
- Empty profiles use the synthetic fixture pack when optional web research is off. Serper search is bound only when both `SERPER_API_KEY` and `AAMAD_ENABLE_WEB_RESEARCH=true`; no LinkedIn, page-scraping, shell, ATS, or message-send tools are bound.
- Final output is checked for required report headings and that it is non-empty and not wrapped in a code fence. Candidate evaluations are advisory; outreach is draft-only.
- API errors are returned in an error envelope. Lifecycle logs include run IDs, status, duration, and error class only; exception text, prompts, candidate profiles, and credentials are not logged.

## Files

- `src/recruitment_assistant/api.py` — FastAPI endpoints, run registry, worker dispatch, timeout and sanitized errors.
- `src/recruitment_assistant/crew.py` — YAML loading, CrewAI assembly, gated Serper tool, fixture injection, report validation.
- `src/recruitment_assistant/config/agents.yaml` and `tasks.yaml` — roles, task prompts, stable task names, expected outputs, and guardrails.
- `src/recruitment_assistant/fixtures.py` — synthetic offline candidate profiles.
- `tests/test_api.py` — health, validation, async success, concurrency, and sanitized failure checks.
- `pyproject.toml` — package and runtime/test dependencies; CrewAI and CrewAI Tools are pinned to the tested `1.15.23` release.

## Run And Test

Install the backend and test dependencies from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

Set `OPENAI_API_KEY` in the process environment, then start the API on localhost:

```powershell
$env:OPENAI_API_KEY = "<your-key>"
python -m uvicorn recruitment_assistant.api:app --app-dir src --host 127.0.0.1 --port 8000
```

Run the offline API tests with `python -m pytest -q`. Tests stub the crew call and do not contact an LLM or search provider.

## Known Gaps

- The browser frontend and integration workflow are separate build work; this backend is not publicly authenticated and must remain local or in an approved controlled demo.
- CrewAI 1.15.23 exposes execution timeout on `Agent`, not `Crew`. Each agent is configured for 480 seconds and the API watchdog enforces the 480-second run-status deadline. Python cannot forcibly stop a synchronous provider call running in a worker thread; if one outlives the deadline, the single-run gate remains occupied until that call returns.
- Prompt bodies are not written to traces because job briefs and profiles can contain personal data. Redacted lifecycle logs are emitted to the service logger; durable Prompt Trace storage and 24-hour cleanup are not implemented.
- Web research is optional and disabled by default. When enabled it uses Serper search only and is not part of offline fixture tests.
- Scores and recommendations are decision support only. No production hiring use, automated disposition, real-candidate dataset, persistence, ATS integration, or outbound communication is supported.

## Sources

- `project-context/1.define/prd.md` — product scope, agent roles, safety policies, runtime settings, and acceptance criteria.
- `project-context/1.define/sad.md` — authoritative three-agent CrewAI design, API contract, run lifecycle, and controls.
- `.cursor/rules/adapter-crewai.mdc` — YAML-first configuration, sequential process, tracing, and CrewAI conventions.
- `src/recruitment_assistant/` and `tests/` — implemented runtime behavior and verification.

## Assumptions

- `AAMAD_TARGET_RUNTIME=crewai` remains the selected runtime; this service is a local/demo MVP, not a public production hiring system.
- Candidate input is synthetic or fixture data. No real candidate PII should be submitted, persisted, or committed.
- The three-agent SAD scope takes precedence over the PRD's earlier four-agent wording; Recommender owns report compilation and draft-only outreach.
- A timed-out synchronous provider call does not need forceful cancellation for the MVP; the API marks the run failed while the worker may remain occupied until the call returns.

## Open Questions

- No blocking questions remain for the documented MVP scope.
- Before any shared deployment, decide access control and whether hard termination of timed-out provider calls is required; the current single-user local service does not provide either guarantee.

## Audit

- **Resolved runtime:** `AAMAD_TARGET_RUNTIME=crewai`.
- **LLM:** `OPENAI_MODEL` (default `gpt-4o`); temperature `0`; max tokens `2048`; credentials from `OPENAI_API_KEY` only.
- **Crew controls:** sequential, agent-level `max_iter=8`, `max_retry_limit=2`, `max_execution_time=480`, crew-level `max_rpm=10`, API run deadline `480`, `memory=False`, `allow_delegation=false`.
- **Web search:** Serper is opt-in via `SERPER_API_KEY` and `AAMAD_ENABLE_WEB_RESEARCH=true`; LinkedIn scraping is prohibited.
- **Prompt Trace:** No runtime prompt or candidate text persisted; lifecycle-only sanitized logging is used.
- **Persona/action:** `backend-eng` / `develop-be`, `define-agents`, `implement-endpoint`, `document-backend`.
- **Timestamp:** 2026-10-02.