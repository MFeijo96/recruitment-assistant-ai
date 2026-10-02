# QA Report: Recruitment Assistant

**Status:** Offline backend checks pass; full browser/provider smoke remains blocked  
**Date:** 2026-10-02  
**Persona/actions:** `@qa.eng` / `*qa`, `*verify-flow`, `*log-defects`, `*future-work`  
**Runtime:** CrewAI; local single-user MVP

## Scope and Result

Reviewed the PRD, SAD, frontend build, backend implementation, and integration artifacts. The backend contract and deterministic fixture preparation pass their current automated checks. The complete browser-to-live-CrewAI workflow was not run: Node.js/npm and frontend dependencies are unavailable, and `OPENAI_API_KEY` is not present in the process environment. No live provider or search calls were made.

| Stage | Command / check | Result | Acceptance coverage |
| --- | --- | --- | --- |
| Unit / crew | `python -m pytest -q tests/test_crew.py` | PASS: 6 passed | AC-P0-2 three sequential agents, context chain and runtime controls; AC-P0-4 default tool binding; AC-P0-5 fixture injection; optional research gating; report-shape rejection |
| Integration / API | `python -m pytest -q tests/test_api.py` | PASS: 7 passed | AC-P0-1 blank-input rejection and accepted kickoff; AC-P0-2 asynchronous run status; AC-P0-7 sanitized failures; health, concurrent-run rejection, unknown run and expiry behavior |
| Combined regression | `python -m pytest -q` | PASS: 13 passed | Same backend coverage, run together |
| Sourcing guardrail | Search of `src/` for `li_at`, `LinkedInTool`, `Selenium`, `send_mail`, and `send_email`; reviewed agent/task YAML | PASS: no prohibited tools in source; prompts prohibit LinkedIn scraping and message sending |
| Browser / UI | Frontend install/build and browser interaction | BLOCKED: `node`, `npm`, and `frontend/node_modules` are unavailable | AC-P0-1 and AC-P0-3 UI acceptance; keyboard interaction, rendered status/error/report, and responsive behavior remain unverified |
| Live fixture run | Real CrewAI kickoff with default fixture pack | NOT RUN: no `OPENAI_API_KEY` in process environment; no provider call attempted | AC-P0-2 and AC-P0-5 runtime end-to-end success remains unverified; fixture injection itself passes unit coverage |
| AAMAD artifact validation | `aamad validate` | FAIL: setup artifact missing and backend artifact missing required `Sources`, `Assumptions`, and `Open Questions` headings. The QA artifact initially also lacked required headings; those were added and revalidated. | Artifact quality gate, not an application runtime failure |

The test commands emitted 11 deprecation warnings in total (CrewAI deprecated API warnings and a Starlette/httpx TestClient warning); these did not fail tests.

## Smoke Flow

The deterministic API test simulates the main flow without contacting external services: submit a valid role brief, receive `202` and a queued run ID, poll to a terminal succeeded state, and receive the expected markdown report. The test suite also verifies blank requirements are rejected, a concurrent run receives `429`, unknown run IDs receive `404`, and crew exceptions are returned without exposing exception contents.

This is an API-level simulated flow, not a browser-to-backend run with a real CrewAI invocation. No generated candidate report was reviewed for content quality.

## Issues and Known Gaps

1. **Browser acceptance is unverified.** The frontend build, keyboard submission, running/success/failure rendering, and responsive behavior could not be exercised because Node.js/npm and installed dependencies are absent.
2. **Live CrewAI completion is unverified.** The fixture-injection path is unit-tested, but no LLM-backed run confirmed that generated output satisfies content expectations. The existing report validator checks required headings and non-empty, unfenced markdown, not the correctness of every claim or outreach draft.
3. **PRD agent-count inconsistency.** The authoritative architecture and implemented workflow define three agents, while the PRD NFR table still describes a fixture run using “4 agents.” Align that wording in a product-document follow-up.
4. **AAMAD artifact quality gate has outstanding findings.** `aamad validate` reports missing `project-context/2.build/setup.md` and missing required sections in `backend.md`. The `qa.md`-missing finding from the initial validation is resolved by this report; rerun validation to confirm the remaining findings.
5. **Dependency deprecations.** Current tests pass with CrewAI and Starlette/httpx deprecation warnings; track dependency/API compatibility during maintenance.

## Future Work

- Install the documented frontend dependencies, run `npm run build`, and perform browser acceptance for keyboard submission, validation, polling, report display, failure messaging, and mobile layout.
- Run one controlled fixture-backed CrewAI flow with an explicitly configured provider credential; use synthetic fixtures only and verify the final report manually.
- Add tests for report content expectations beyond headings, including evidence-based rationale, uncertainty/contact labels, advisory language, and draft-only outreach.
- Resolve the PRD four-agent wording and the outstanding AAMAD artifact validation findings.
- Complete the required security assessment before Deliver; QA did not perform a security assessment or performance testing.

## Exit Recommendation

Backend/API behavior is acceptable for offline MVP checks. Do not treat the chat workflow as fully acceptance-tested until browser verification and a controlled provider-backed fixture run pass. Keep use local/demo-only with synthetic data; complete the required security assessment before Deliver.

## Sources

- `project-context/1.define/prd.md` — acceptance criteria and MVP boundaries.
- `project-context/1.define/sad.md` — architecture, API and runtime contracts.
- `project-context/2.build/frontend.md` — UI implementation and pending frontend verification.
- `project-context/2.build/backend.md` — backend implementation and known runtime constraints.
- `project-context/2.build/integration.md` — FE/API flow and integration notes.
- `tests/test_api.py` and `tests/test_crew.py` — automated checks executed for this report.
- `.cursor/agents/qa-eng.md` — QA persona requirements and report structure.

## Assumptions

- Offline tests with a stubbed crew are valid for API contract verification, but do not establish live provider success.
- The first environment remains local/demo and uses only synthetic or bundled fixture profiles.
- No frontend or provider setup was installed or modified as part of this QA run.

## Open Questions

- When Node.js/npm and frontend dependencies are available, who will run and record browser acceptance?
- When an approved provider credential is available, who will run the controlled fixture-backed CrewAI smoke and review generated report content?

## Audit

- **Resolved runtime:** `AAMAD_TARGET_RUNTIME=crewai`.
- **Timestamp:** 2026-10-02.
- **Persona/actions:** `qa-eng` / `qa`, `verify-flow`, `log-defects`, `future-work`.
- **Validation:** 6 crew tests and 7 API tests passed; full `python -m pytest -q` passed with 13 tests.
- **Limitations:** Frontend/browser and live-provider checks were blocked or not run as recorded above; no credentials or provider calls were used.