# Solution Architecture Document: Recruitment Assistant

**Status:** Define-phase architecture baseline  
**PRD:** [project-context/1.define/prd.md](prd.md)  
**MRD:** [project-context/1.define/mrd.md](mrd.md)  
**Selected runtime:** `crewai`

## 1. MVP Architecture Philosophy & Principles

### MVP Design Principles

- Deliver one recruiter workflow: submit a job brief, run a bounded agent crew, review one explainable shortlist report.
- Keep the runtime and API in one Python service and the browser UI as a separate, thin client.
- Use sequential orchestration and explicit data contracts; no agent-to-agent delegation or long-lived agent memory.
- Default to fixtures and synthetic candidate profiles. Human review is mandatory; the system never decides whom to hire or reject.
- Make run state and failures visible. Do not log raw candidate profiles, prompts containing personal data, credentials, or tool payloads.

### Stakeholders and Concerns

| Stakeholder | Primary concern | Architectural response |
| --- | --- | --- |
| Recruiter / TA coordinator | Fast, useful shortlist with evidence and understandable errors | Web chat, ranked markdown report, visible status, reasons and uncertainty labels |
| Hiring manager | Concise, reviewable recommendation | Final report is readable without access to internal crew configuration |
| Project operator | Reproducible, low-risk local/demo setup | Fixture-first execution, environment-based secrets, one-process deployment |
| QA / AAMAD build personas | Deterministic behavior traceable to acceptance criteria | YAML agent/task configuration, stable task IDs, fixture tests and run diagnostics |
| Candidates / affected people | Privacy, fairness, no unreviewed automated disposition | Synthetic/fixture-only first environment, no auto-reject, no external contact send |

### Core vs Future Features

**MVP:** web chat kickoff; three sequential CrewAI agents; fixtures or optional operator-provided synthetic profiles; optional gated public-web research; scores with justifications; final recruiter markdown report; ephemeral run state; health endpoint.

**Future / excluded:** ATS, CRM or candidate database; CSV or resume-PDF ingestion; official job-board/LinkedIn integrations; LinkedIn cookie or Selenium access; outbound email/InMail; scheduling; OAuth, SSO, multi-tenancy; persistent history; public production use; bias-audit and legal deployment package; horizontal scaling.

### Technical Architecture Decisions

| Decision | Choice | Rationale |
| --- | --- | --- |
| Runtime | CrewAI, sequential | Matches the selected adapter, Python project default, and repeatable task graph. |
| Crew size | Researcher, Evaluator, Recommender | Matches the user request and PRD Section 6. Recommender compiles the report and draft-only outreach where required; no separate Communicator or Reporter agent in this SAD. |
| Frontend | React + Vite + TypeScript | A small web chat is explicitly required by the PRD; this keeps the client simple and separate from the Python API. No vendor UI library is mandatory. |
| Backend | FastAPI + Pydantic request/response models | Python-native API boundary with explicit validation and typed contracts for CrewAI. |
| Long-running kickoff | Accepted run + status polling | Returns an acknowledgement within the PRD's <3s target without holding the browser request for up to 480s. |
| Persistence | In-memory run registry only | Meets single-user demo and session-only retention requirements without introducing a database. |
| Streaming | Not required for MVP | Status polling and a working indicator meet the UX need without coupling the API to runtime-specific token streaming. |

### System Context and Boundaries

The system is a single-user local/demo recruiter tool. The browser communicates only with the FastAPI service. The service validates a run, invokes CrewAI, and may call the configured LLM provider; optional search is enabled only when both `SERPER_API_KEY` is present and `AAMAD_ENABLE_WEB_RESEARCH=true`. Candidate data and run results are transient. No ATS, messaging service, candidate-facing application, or system of record is in scope.

**External actors / systems:** recruiter browser; LLM provider via `OPENAI_API_KEY` and `OPENAI_MODEL`; optional Serper search. **Trust boundary:** all browser input and model/tool output are untrusted; validate schemas and render report markdown safely.

## 2. Multi-Agent System Specification

### Agent Architecture

Agents and tasks are defined in `config/agents.yaml` and `config/tasks.yaml`; Python code composes and executes the CrewAI crew. Use stable IDs, explicit required output headings, and ephemeral run-scoped result locations. Agent configuration must not contain credentials.

| Agent / task | Goal and inputs | Output contract / guardrails |
| --- | --- | --- |
| `researcher` / `research_candidates_task` | Find up to 10 relevant candidate profiles using `job_requirements`, optional `candidate_profiles`, the fixture pack, or gated approved public sources. | Candidate list with evidence/source where available, brief suitability, and contact data only when supplied or publicly cited; otherwise label `unknown - verify`. Never use LinkedIn cookie/Selenium access. |
| `evaluator` / `evaluate_candidates_task` | Compare each researched profile with the job requirements. | Per-candidate structured score, strengths, gaps, and written evidence-based rationale. Scores are advisory; do not infer protected traits or issue disposition decisions. |
| `recommender` / `recommend_candidates_task` | Rank candidates and assemble the recruiter-facing result from evaluation and research context. | Markdown report with ranked recommendations, score justifications, evidence/uncertainty labels, and draft-only outreach templates where required by PRD P0 acceptance criteria. No send action. Output has no enclosing code fence. |

### Task / Turn Orchestration

1. Validate non-empty `job_requirements`; use optional `candidate_profiles` as free text, defaulting to an empty string.
2. If profiles are empty and web research is disabled, inject the bundled deterministic fixture pack (PRD AC-P0-5).
3. Run `research_candidates_task`, then `evaluate_candidates_task`, then `recommend_candidates_task` using explicit `Task.context` dependencies.
4. Return the final report through the run-status API. Keep terminal run data in memory for at most 15 minutes after the last status poll; expire it on idle timeout, delete an older completed run when a new run is accepted, and clear all run data on process shutdown. No request, intermediate output, or report is written to durable storage.

**Runtime controls:** `Process.sequential`; `memory=False`; `allow_delegation=false`; `max_iter=8` per task (never above adapter baseline 12); `max_retry_limit=2` minimum; `max_rpm=10`; `max_execution_time=480` seconds per kickoff. Do not retry provider failures without bound. A run exceeding its cap fails with a user-readable timeout diagnostic; no partial result is presented as successful.

**Guardrails:** validate required report sections and candidate count; enforce draft-only outreach; mark unverified contacts; prohibit LinkedIn cookie tools and shell access; keep tools least-privileged. Optional research tools are not bound unless both the key and feature flag are set. No outbound communication tool is bound.

**Failure and cancellation:** Crew/provider/guardrail failures move the run to `failed` with a sanitized error code and message. The MVP does not promise forceful cancellation of an in-flight CrewAI call; the 480s hard cap is the termination bound. A stop control and runtime-specific cancellation are deferred unless confirmed feasible during implementation.

### Runtime-Conditional Configuration: CrewAI

- `crew.py` (or equivalent) loads YAML definitions and creates one sequential crew.
- Tasks declare stable IDs, expected output headings, and context chaining: evaluator context includes research; recommender context includes research and evaluation.
- Use run-scoped transient results (conceptually `run:{run_id}/research_candidates_task`, `.../evaluate_candidates_task`, `.../recommend_candidates_task`). Do not write raw candidate artifacts to persistent task output files.
- Keep agent/task YAML version-controlled. Tool references are validated before kickoff. Model/provider settings are read from environment variables.
- Capture required Prompt Trace / lifecycle events in a redacted trace path under `project-context/2.build/logs`; never persist secrets or raw candidate PII. Retention is at most 24 hours. The initial environment is restricted to synthetic/fixture data, consistent with PRD/MRD.

### Logical View: Elements and Rationale

| Element | Responsibility | Rationale |
| --- | --- | --- |
| Chat UI | Compose role requirements, show run state, display report/error | Primary PRD workflow; no separate dashboard needed |
| FastAPI service | Validate requests, reserve run slot, expose run status and health | Clear browser/runtime boundary; quick acknowledgement |
| In-memory run registry | Hold transient status and result for the active session | Meets one-run concurrency and no-persistence requirements |
| CrewAI adapter | Load YAML and execute sequential tasks with controls | Uses the selected runtime semantics directly |
| Fixture pack | Deterministic candidate inputs for demo and tests | No network or real-candidate data required for baseline |
| LLM / optional search | Generate assessments; optionally find approved public information | External integrations limited to those permitted by PRD |

## 3. Frontend Architecture Specification

### Technology Stack

- React, Vite, and TypeScript for the web client; use semantic HTML and the project's minimal/system visual direction.
- Keep UI state in memory for the current session. No browser persistence of candidate profiles or reports.
- Render report markdown with a maintained safe renderer or escaped text; disallow unsafe HTML and external embeds.

### Application Structure

- One primary chat/run page; no candidate portal or dashboard routes in MVP.
- Components: job-requirements composer, optional synthetic profile input, submit/status area, advisory notice, report renderer, and accessible error state.
- API client owns request serialization and polling. Components do not call CrewAI or provider APIs directly.
- The frontend epic builds against the API contract below; integration wires it to FastAPI.

### Interface Requirements

- Accept a non-empty job brief. Profiles remain optional free text; no CSV upload.
- Show working state while a run is queued/running and render the final markdown on success.
- Clearly label output as advisory and requiring recruiter/human review; do not present an auto-hire or auto-reject action.
- Show actionable validation, provider, timeout, and generic run failures as text, not color alone.
- Keyboard-submittable controls, readable contrast, responsive desktop-first layout, and WCAG 2.2 AA target where the chosen stack permits.
- Streaming, task-by-task progress, report download, and stop/cancel are deferred; a generic working indicator is sufficient for MVP.

## 4. Backend Architecture Specification

### API Architecture

Base path: `/api`. JSON over HTTP; no token streaming in MVP.

| Method / path | Request | Success response | Behavior |
| --- | --- | --- | --- |
| `POST /api/runs` | `{ "job_requirements": "...", "candidate_profiles": "..." }`; `candidate_profiles` optional | `202 { "run_id": "...", "status": "queued" }` | Reject blank requirements with `400`; reject a second concurrent kickoff with `429`; reserve a run and start the bounded crew. |
| `GET /api/runs/{run_id}` | None | `{ "run_id": "...", "status": "queued|running|succeeded|failed", "report_markdown": "...", "error": { "code": "...", "message": "..." } }` | Include `report_markdown` only on success and `error` only on failure. Unknown/expired run IDs return `404`. |
| `GET /healthz` | None | `{ "status": "ok" }` | Process liveness only; does not claim external provider availability. |

The POST handler acknowledges promptly and delegates blocking CrewAI execution to a bounded worker in the same process. The single-process deployment has one active run; concurrent requests receive `429` rather than accumulating an unbounded queue. Run data is process-local and not durable. On restart, prior run IDs expire. Apply request validation, safe error mapping, and local-development CORS restricted to the configured frontend origin; no public unauthenticated deployment is approved.

Error envelope: `{ "error": { "code": "validation_error|run_busy|run_not_found|crew_failed|provider_failed|timeout", "message": "..." } }`. Do not expose stack traces, provider secrets, prompt text, or raw tool payloads to clients.

### Data Architecture

- No database, vector store, or durable candidate repository in MVP.
- Run status and outputs live only in the API process. Expire terminal run data after 15 minutes without a status poll, delete an older completed run when a new run is accepted, and clear all state on process restart. This bounded idle expiry defines session end when browser closure cannot be detected reliably.
- Fixture data is synthetic and version-controlled. Do not add real candidate profiles or PII to Git, tests, traces, or sample artifacts.
- Persist only redacted diagnostics/traces as allowed by PRD: maximum 24-hour retention in `project-context/2.build/logs`; request/response bodies are not retained beyond the session.

### Runtime Integration Layer

- A runtime service maps validated API input to `crew.kickoff(inputs={"job_requirements": ..., "candidate_profiles": ...})`.
- Load agent/task YAML once per process or per run with validation before kickoff; tool bindings follow the opt-in policy.
- Isolate synchronous CrewAI work from the API event loop using a bounded worker. Enforce one active kickoff and the 480-second runtime limit.
- Record task lifecycle, duration, provider/model identity, token/cost metrics where available, retries, and guardrail outcomes without logging candidate text or secrets.

### Authentication and Secrets

MVP is local/dev, single-user, with no SSO. Bind to localhost for local use; any shared deployment requires an access-control decision before exposure.

Read credentials/settings from environment variables only: required `OPENAI_API_KEY`; optional `OPENAI_MODEL` (default `gpt-4o`); optional `SERPER_API_KEY`; optional `AAMAD_ENABLE_WEB_RESEARCH` (default `false`); `AAMAD_TARGET_RUNTIME=crewai`. The local `.env` is ignored by Git; `.env.example` contains names and placeholders only. Never include actual key values in this document or Prompt Trace.

## 5. DevOps & Deployment Architecture

- **Build/CI:** Python dependency installation, formatting/lint and type checks, unit tests, API/crew integration tests, and frontend lint/build. Map tests to PRD AC IDs; baseline fixture tests must not call external search or LinkedIn.
- **Hosting:** local development first; one process on a developer machine or one small VM/container for a controlled demo. Do not run multiple API workers because run coordination is in-memory.
- **Health:** expose `/healthz` for process liveness. Deployment secrets come from environment injection; do not bake `.env` or secrets into images.
- **Operations:** pin CrewAI and provider dependencies, document model/runtime settings, and inspect sanitized failure/duration/cost metrics. External provider downtime fails the run visibly.
- **Deferred:** production CI/CD promotion, infrastructure-as-code, multi-region/high availability, autoscaling, persistent queue, advanced APM, backup/recovery, and multi-tenant isolation. Complete the configured security assessment before Deliver.

## 6. Data Flow & Integration Architecture

### Process / Runtime View

```text
Recruiter browser
    | POST job brief / optional synthetic profiles
    v
FastAPI validation and one-run gate
    | 202 run_id; status polled by browser
    v
In-memory run registry -> CrewAI sequential crew
                               |
                               +-> Researcher -> Evaluator -> Recommender
                               |       ^                          |
                               |       |                          +-> final markdown
                               |   fixture pack                   |
                               |   or optional Serper             |
                               v                                  v
                         LLM provider <----------------------- report result
                                                                  |
Browser GET run status <------------------------------------------+
```

### Integration Points

| Integration | MVP policy |
| --- | --- |
| OpenAI-compatible LLM | Required; key from `OPENAI_API_KEY`; model defaults to `gpt-4o` and may be overridden by `OPENAI_MODEL`. |
| Fixture candidate pack | Default deterministic source when profiles are empty and web research is off; no network required. |
| Serper / approved public web | Optional only when both `SERPER_API_KEY` and `AAMAD_ENABLE_WEB_RESEARCH=true`; use minimum read-only search tools and public non-LinkedIn sources. |
| Serper search | Optional only when both `SERPER_API_KEY` and `AAMAD_ENABLE_WEB_RESEARCH=true`; bind search only (no page-scraping tool). Use publicly accessible, non-LinkedIn, non-gated sources; include source URLs and treat snippets as unverified evidence. |
| LinkedIn | No cookie/Selenium scraping. Official APIs are deferred. |
| ATS, email, calendar | Not integrated in MVP; no data push or message send. |

Browser input passes to the API, is validated and placed in the run registry, then mapped to CrewAI kickoff inputs. Outputs flow through the three tasks into one report. The browser polls status until success/failure. Errors are sanitized at the API boundary and displayed to the recruiter. Optional external calls are server-side only; API keys are never sent to the browser.

## 7. Performance & Scalability Specifications

| Measure | MVP target / control |
| --- | --- |
| Submit acknowledgement | <3 seconds (PRD); return accepted run ID before crew completion |
| End-to-end run | Maximum 480 seconds; timeout produces a visible failure |
| Concurrent kickoffs | One; reject additional request with `429` |
| Crew rate / iteration | `max_rpm=10`; `max_iter=8` per task, capped at 12 |
| Retries | `max_retry_limit >= 2`; bounded, no unbounded provider retry |
| Availability | Local/demo only; no production SLA |

Cost is primarily model and optional search usage. Record token/cost metadata per run where provider/runtime exposes it, without storing prompts or candidate content. Scaling beyond one process requires moving run coordination to a durable shared queue/store; that is deferred and out of scope.

## 8. Security & Compliance Architecture

- **AuthN/AuthZ:** local single-user only; bind to localhost. No public or production hiring deployment without a separate access-control and governance design.
- **Data policy:** use fixtures or synthetic profiles only in the first environment. Treat names, contact details, and resume-like text as PII; do not commit, persist, or log real candidate data.
- **Secrets:** environment-only; `.env` excluded from Git, `.env.example` placeholders only. Redact credentials from exceptions, traces, and diagnostics.
- **Input/output safety:** validate request shape and required text; treat profile text and model/tool output as untrusted; safely render markdown; do not expose stack traces or unsafe HTML.
- **Least privilege:** no shell tool, no LinkedIn scraping, no send-mail tool. Search is disabled unless explicitly enabled with both required settings.
- **Human oversight:** label all evaluations advisory; require recruiter review; no automated reject/hire decision and no outbound contact.
- **Trace retention:** redacted lifecycle/Prompt Trace only, at most 24 hours in the specified build log location; discard session request/response bodies.
- **Compliance boundary:** PRD excludes production hiring use in EU/UK/NYC and other jurisdictions. Legal review, DPIA, bias audit/notice workflows, and applicable high-risk AI obligations are prerequisites for any future production use, not claims of this MVP.

## 9. Testing & Quality Assurance Specifications

- **Unit:** required-field validation; optional profile handling; fixture injection; environment-gated tool binding; output/section validation; markdown-safe rendering; error mapping and cleanup.
- **Crew integration:** assert three YAML agents and tasks load; sequential order and context chain; controls are configured; no LinkedIn cookie tool; run fixture workflow without network; verify score rationales and unverified-contact labels.
- **API integration:** accepted kickoff/status transitions; blank input `400`; second active run `429`; unknown/expired ID `404`; success report shape; provider/timeout failures return sanitized diagnostics; health endpoint responds.
- **Frontend acceptance:** keyboard submit; working state/polling; report/error rendering; advisory notice; responsive layout and accessible text errors.
- **Security checks:** scan committed artifacts for secrets and PII; ensure `.env` is ignored and `.env.example` contains placeholders; confirm no shell, ATS, LinkedIn scrape, or send tools are bound.
- **Smoke:** launch local frontend and API, run fixture-backed kickoff, read report, confirm process health. Any live-provider check is manual/opt-in and not required for CI.
- Required security assessment before Deliver per `aamad.config.example.yml`.

### PRD Traceability

| Requirement | Architectural element / verification |
| --- | --- |
| AC-P0-1 kickoff | `POST /api/runs`, required non-empty `job_requirements`, optional `candidate_profiles`; validation tests |
| AC-P0-2 sequential crew | Three sequential tasks with explicit context; crew integration test |
| AC-P0-3 report | Recommender returns markdown report, reasons, outreach drafts if included, advisory UI; API/UI acceptance test |
| AC-P0-4 safe sourcing | No LinkedIn cookie/Selenium binding; configuration test |
| AC-P0-5 fixture path | Fixture pack injected when profiles absent and web is off; offline integration test |
| AC-P0-6 secret hygiene | Environment variables and placeholder-only `.env.example`; repository secret scan |
| AC-P0-7 errors | Sanitized status/error envelope; provider/timeout/failure tests |
| PRD NFR / UX | 3s acknowledgement, 480s cap, concurrency one, keyboard access, textual error and working state tests |

**Scope decision:** This release uses three agent objects: Researcher, Evaluator, and Recommender. Recommender performs report compilation and required draft-only outreach; it never sends messages. The PRD and MRD were synchronized on 2026-10-02 to make this three-agent workflow authoritative. The four-agent CrewAI example remains reference material, not the product contract.

## 10. MVP Launch & Feedback Strategy

- **Pilot:** internal/demo only, using bundled fixtures or synthetic candidate profiles; no live requisition or real candidate PII.
- **Entry criteria:** fixture kickoff succeeds; report contains evidence-based scores and uncertainty labels; failures are visible; security assessment is complete before Deliver.
- **Success measures:** fixture kickoff completion in CI; submit-to-report completion in one chat session; recruiter review confirms the report is usable as decision support. No acceptance-rate instrumentation is required in MVP.
- **First iteration priorities:** verify the three-agent report schema with QA, then consider P1 task progress events and markdown download. Do not add ATS or outbound messaging to this release.
- Public production deployment is a no-go until privacy, legal, security, and bias assessment requirements are separately approved.

## Architecture Validation Checklist

- [x] PRD requirements mapped to architectural components and tests.
- [x] Three-agent CrewAI workflow defined consistently across MRD, PRD, SAD, and backend YAML.
- [x] Frontend and backend contracts agree on asynchronous run/status/report flow.
- [x] Secrets are environment-only; sample values are placeholders.
- [x] MVP and future scope are explicitly separated.
- [x] Resolved `AAMAD_TARGET_RUNTIME=crewai` recorded in Audit.

## Sources

1. `project-context/1.define/prd.md` — primary product requirements, acceptance criteria, NFR, UX and resolved product decisions.
2. `project-context/1.define/mrd.md` — target users, runtime recommendation, safety and deployment constraints.
3. `.cursor/templates/sad-template.md` — required SAD structure.
4. `.cursor/rules/adapter-crewai.mdc` — CrewAI YAML, orchestration, controls, tracing, guardrails and failure policy.
5. `.cursor/agents/system-arch.md` — architecture persona and output requirements.
6. `aamad.config.example.yml` — Python/CrewAI defaults, testing, security assessment, UI preferences.

## Assumptions

- FastAPI and React/Vite/TypeScript are architecture defaults because the PRD requires a web chat and Python is the configured primary language; the PRD does not prescribe framework vendors.
- The frontend and backend run locally or in one controlled demo environment. Shared deployment requires an access-control decision.
- The Recommender compiles final markdown and draft-only outreach without a separate agent; this is documented in MRD-Q9 and PRD-Q9.
- The official four-agent example is reference material. The three-agent design is authoritative across product and architecture artifacts.
- Terminal run results expire after 15 minutes without status polling; a new run deletes an older completed result, and process restart clears all state.
- Optional web research uses Serper search only, and only for public, non-LinkedIn, non-gated sources. No page-scraping tool is bound in MVP.

## Open Questions

No architecture decisions remain open for the MVP. The following decisions close the prior questions:

- **Agent count:** three agents are authoritative; Recommender combines reporting and draft-only outreach. MRD and PRD were synchronized to this decision on 2026-10-02.
- **Public research:** optional Serper search only; public, non-LinkedIn, non-gated sources; no page scraping. Disabled unless both required environment settings are present.
- **Run cleanup:** in-memory terminal results expire after 15 minutes of status-poll inactivity, are removed when a new run is accepted, and are cleared at process shutdown.

## Audit
- **Resolved runtime:** `AAMAD_TARGET_RUNTIME=crewai` (confirmed in root `.env`; aligned with `aamad.config.example.yml` `runtime.target`).
- **Timestamp:** 2026-10-02
- **Persona id:** `system-arch`
- **Action:** `create-sad`
- **Sources reviewed:** PRD, MRD, SAD template, CrewAI adapter rules, System Architect persona, AAMAD example config.
- **Architecture choices:** CrewAI sequential, three agents, FastAPI, React/Vite/TypeScript, asynchronous run/status API, in-memory session state.
- **Prompt Trace:** Omitted; no application prompts or candidate information were generated for this artifact.