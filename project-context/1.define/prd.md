# Product Requirements Document: Recruitment Assistant

**Deep Research Report / MRD:** `project-context/1.define/mrd.md`  
**System Description:** N/A (elicitation not run; stakeholder specified CrewAI recruitment example)  
**System Concept:** Recruiter chat MVP that kicks off a sequential multi-agent crew to research or ingest candidates, score them against job requirements, draft outreach, and compile a markdown shortlist report.  
**Selected Runtime:** `crewai` (resolved default; product definition remains adapter-portable)

---

## 1. Executive Summary

### Problem Statement

Talent acquisition teams still spend most of a requisition cycle on **manual sourcing, inconsistent screening, and one-off outreach writing**. SHRM 2025: **69%** of organizations struggle to fill full-time roles; median **time-to-fill ~1.5 months**. Recruiters typically see only a **fraction** of applicants (SHRM commentary on screening). Generative AI is already saving ~**20% of the workweek** for TA pros who use it (LinkedIn Future of Recruiting 2025), but enterprise ATS AI is expensive, opaque, and tied to a system of record.

**Quantified impact (directional, from MRD):** delayed fill increases overtime, lost productivity, and cost-per-hire; ghosting and thin pipelines waste sourced leads. Target users for MVP: **internal recruiters / TA coordinators** (and hiring managers as report readers). Market population for a later commercial SKU: organizations buying recruitment software (~USD 2.5–3.8B 2025/26 publishers’ range) and the smaller AI-recruitment slice (~USD 0.6–0.75B). **MVP itself is an internal/operational copilot**; commercial GTM is Future Work.

### Solution Overview

A **three-agent sequential crew** productized for the MVP:

1. **Job Candidate Researcher** — produce a list of potential candidates (from operator-supplied profiles and/or allowed public research — **not** LinkedIn cookie scrape).
2. **Candidate Evaluator** — assess job-related evidence and provide advisory scores with written justifications.
3. **Candidate Recommender** — rank candidates, draft outreach templates, and compile the recruiter markdown report. No messages are sent.

The Recommender combines outreach drafting and reporting from the four-role CrewAI reference example; the user-visible outputs remain unchanged.

**Differentiators vs ATS copilots / LinkedIn Hiring Assistant:** explicit task graph, YAML-defined roles, citations in-report, AAMAD-auditable traces, works without an ATS. **Not a differentiator:** size of a talent graph.

**Expected outcomes:** one-session shortlist artifact; recruiter time shifted from compilation to judgment; zero unsupervised hiring decisions.

### Strategic Rationale

Multi-agent is optimal because the example (and real TA work) is a **pipeline of specialist skills** with a merge step — sequential CrewAI `Task.context` matches that. ROI for MVP is **operator time and a reusable AAMAD reference app**, not ARR. Timing: SHRM AI-in-HR **43%** (2025) and LinkedIn GenAI **37%** support a copilot, while EU AI Act / NYC LL144 require **HITL** positioning now.

---

## 2. Product Overview

The Recruitment Assistant is a recruiter-focused, AI-assisted workflow that helps teams turn a job specification into a prioritized shortlist of candidates. The product is designed as a lightweight multi-agent experience that combines sourcing, evaluation, and recommendation into a single recruiter-facing workflow.

At a high level, the product accepts a job requirement, identifies candidate options from approved sources or operator-provided profiles, evaluates fit against the role, and presents ranked recommendations with supporting rationale. The core value proposition is not fully automated hiring; it is structured decision support that reduces manual effort while keeping the recruiter in control.

The product is intended to help recruiters move faster from role intake to shortlist review without relying on a heavy enterprise ATS or opaque black-box scoring.

### Core Value Proposition

- Reduce time spent manually researching candidates and comparing profiles
- Improve consistency in resume-to-role evaluation
- Surface ranked recommendations with explainable reasoning
- Support recruiter and hiring-manager review in a single workflow
- Deliver a practical MVP that is safe, traceable, and easy to extend

---

## 3. Goals and Success Metrics

The Recruitment Assistant is designed to improve recruiter productivity and consistency while keeping decision-making human-led.

### Primary Goals

1. Reduce the time to source and shortlist candidates for a role.
2. Improve the consistency and quality of candidate-to-job matching.
3. Increase recruiter confidence in the shortlist by providing rationale and ranked recommendations.
4. Create a reusable internal demo and prototype that can evolve into a broader TA workflow product.

### Success Metrics

| Goal | Metric | Target / Direction |
| --- | --- | --- |
| Time to source candidates | Time from job brief to shortlist | Reduce manual sourcing effort materially vs baseline workflow |
| Candidate match accuracy | Quality of shortlist relative to role criteria | Improve consistency of fit assessment across recruiters |
| Recruiter satisfaction | Ease of use, trust, and perceived value | Positive feedback on shortlist quality and clarity of recommendations |
| Completion rate | Successful kickoff → report generation | High success rate for fixture-based and low-complexity demo runs |

The MVP should be measured primarily on workflow efficiency and decision support quality rather than on fully automated hiring outcomes.

---

## 4. User Personas

### Primary Persona: Recruiter

**Role:** Recruiter or TA coordinator

**Needs:**
- Find qualified candidates quickly for a role
- Compare candidates against job requirements consistently
- Shortlist candidates with evidence and rationale
- Reduce repetitive manual sourcing effort

**Main goal:** Create a strong shortlist in a single workflow without manually stitching together multiple tools.

### Secondary Persona: Hiring Manager

**Role:** Hiring manager or decision stakeholder

**Needs:**
- Review ranked candidate recommendations quickly
- Understand why a candidate is a strong or weak fit
- Receive a concise recruiter-ready summary without manual report assembly

**Main goal:** Review a credible shortlist and decide whom to interview next.

### Supporting Persona: HR / Ops Team

**Role:** Team responsible for shared recruiting workflow and process quality

**Needs:**
- Repeatable hiring support without excessive operational overhead
- Consistent screening and assessment patterns across roles
- A safe, explainable AI process that remains under human control

---

## 5. Core Features

### Candidate Search Based on Job Requirements
- Accept a job requirement or role brief as the primary input
- Search or gather candidate candidates from approved sources and/or operator-supplied profiles
- Support deterministic fixture-based runs for demo and QA

### Automated Candidate Evaluation
- Evaluate candidate fit against skills, experience, and role requirements
- Produce structured scorecards and written reasoning
- Highlight strengths, gaps, and risk areas for each candidate

### Ranked Candidate Recommendations
- Rank candidates based on role fit and evidence
- Present the most relevant recommendations first
- Show why each candidate is recommended or deprioritized

### Integration with Job Posting Systems (Optional for the Mini-Project)
- Allow optional connection to posting or sourcing systems as a future enhancement
- Keep the initial MVP lightweight and self-contained
- Prefer optional integrations after core recruiting workflow is validated

---

## 6. Application Crew Definition

The application-level crew for this mini-project is defined around the core recruiting decision workflow. The product-level crew includes the following specialized roles:

### Researcher Agent
**Purpose:** Search and source candidates based on the job requirement.

Responsibilities:
- Identify candidates or candidate profiles relevant to the role
- Work from approved sources, operator-provided profiles, or fixture data
- Gather candidate context needed for evaluation

### Evaluator Agent
**Purpose:** Evaluate candidate fit against role criteria.

Responsibilities:
- Compare candidate backgrounds to required skills and experience
- Produce consistent scores with supporting rationale
- Call out missing qualifications, weak signals, or misalignments

### Recommender Agent
**Purpose:** Produce ranked candidate recommendations.

Responsibilities:
- Prioritize candidates based on fit and evidence
- Generate the shortlist for recruiter review
- Surface the strongest recommendations first with explainable rationale

This mini-project keeps the crew intentionally focused on sourcing, evaluating, and recommending candidates while leaving full outreach and ATS automation for later phases.

---

## 7. Development Crew Mapping

The project follows the AAMAD team model and maps the required product and implementation responsibilities as follows:

- `@product-mgr` — owns product definition, requirements, and prioritization in the Define phase
- `@system.arch` — designs the technical architecture and system boundaries
- `@backend.eng` — implements the core recruiting workflow and runtime services
- `@frontend.eng` — creates the recruiter-facing chat and reporting experience
- `@integration.eng` — connects the workflow to APIs, data sources, and system interfaces
- `@qa.eng` — validates behavior, acceptance criteria, and regression coverage (Module 06)
- `@devops.eng` — handles delivery, deployment, environment, and operations (Module 07)

This mapping ensures the product and implementation responsibilities remain clear across the Define, Build, and Deliver phases of the project.

---

## 8. Out of Scope (Mini-Project)

The following items are intentionally excluded from this mini-project scope:

- Full ATS integration
- Candidate communication automation or bulk email sending
- Advanced analytics and reporting dashboards
- Multi-tenant enterprise deployment
- Large-scale sourcing network integration
- Candidate portal or applicant-facing workflows
- Deep compliance/monitoring features beyond the MVP guardrails

These items may become future enhancements after the core recruiting workflow is validated and the operational model is proven.

---

## 9. Market Context & User Analysis

### Target Market / Users

**Primary persona — Recruiter (TA coordinator)**

- Owns a requisition; pastes job requirements; needs a ranked shortlist and outreach drafts in one sitting.
- Pain: context switching across LinkedIn, ATS, docs, email.
- Success: trusted scores with evidence; copy-paste ready messages.

**Secondary persona — Hiring manager**

- Consumes the reporter output; does not kick off the crew in MVP (P1: share/export).

**Tertiary — Platform operator / developer**

- Runs AAMAD MVP locally; sets LLM keys; uses fixtures for QA.

**Market size / geography:** See MRD. MVP geographic focus: **unspecified**; design as if EU/US candidate data may appear (conservative privacy). Expansion: ATS connectors, official APIs.

### User Needs Analysis

| Pain | Need |
| --- | --- |
| Inconsistent scoring | Rubric-like scores + justification per candidate |
| ToS/legal fear of scraping | No unofficial LinkedIn automation |
| Black-box AI | Task-level artifacts and report sections |
| Time to first shortlist | Chat kickoff → single report |
| Accidental spam | Drafts only; human send |

**Journey:** Compose JD/requirements → submit in chat → observe running/failed status → read report → edit scores mentally → copy outreach → (out of band) contact candidate.

**Adoption:** Demo fixture run; disclaimer “decision support”; no auto-reject.

### Competitive Landscape

| Alternative | Role vs this product |
| --- | --- |
| Greenhouse / Lever / Workday / iCIMS AI | System of record; heavier; less portable crew |
| LinkedIn Recruiter + Hiring Assistant | Network access we will **not** scrape |
| HireEZ / SeekOut / Gem / Juicebox | Sourcing scale |
| HireVue / Paradox | Interview / high-volume chat |
| Raw CrewAI example CLI | No chat MVP, unsafe LinkedIn tool |
| Manual Google + spreadsheet | Baseline this copilot replaces for **report assembly** |

**Pricing benchmarks:** Not set for MVP (internal). A later commercial copilot, if any, should price **below** bundled Recruiter + ATS AI seats (non-binding; no SKU in this program).

---

## 10. Technical Requirements & Architecture

### Runtime & Agent Specifications

- **Runtime for Build:** `crewai` per adapter-crewai (YAML `config/agents.yaml`, `config/tasks.yaml`, `crew.py`, sequential process).
- **Collaboration:** Sequential; evaluator context includes research, and recommender context includes research and evaluation.
- **Delegation:** `allow_delegation=false` for all three agents (adapter default).
- **Memory:** `memory=False` for reproducibility.
- **Controls (adapter baseline):** `max_iter = 8` (≤ 12); `max_retry_limit >= 2`; crew `max_rpm = 10`; `max_execution_time = 480` seconds per kickoff.
- **Other runtimes:** Preserve the same three product roles if `AAMAD_TARGET_RUNTIME` changes; do not redefine the product as “only CrewAI.”

### Core Agent Definitions

**agent:** `researcher`  
**role:** Job Candidate Researcher  
**goal:** Find potential candidates for the job  
**tools (MVP):** None by default (fixture or `candidate_profiles`). Bind `SerperDevTool` / `ScrapeWebsiteTool` only when **both** `SERPER_API_KEY` and `AAMAD_ENABLE_WEB_RESEARCH=true`. **Prohibited:** LinkedIn cookie (`li_at`) Selenium tool from the example.  
**runtime notes:** `allow_delegation=false`; `verbose` as needed for traces (redact PII in persisted logs).

**agent:** `evaluator`  
**role:** Candidate Evaluator  
**goal:** Compare candidates with job requirements and provide transparent, evidence-based advisory scores.  
**tools:** Same web-research policy as researcher; **do not scrape LinkedIn**.  
**runtime notes:** Scores are advisory; do not infer protected traits or make disposition decisions.

**agent:** `recommender`  
**role:** Candidate Recommender  
**goal:** Rank candidates and compile a recruiter-facing report with draft-only outreach templates.  
**tools:** None by default; approved public search remains opt-in and server-side. No send-mail tool.  
**runtime notes:** Include evidence, uncertainty, score rationale, and human-review notice. Return markdown without enclosing code fences.

### Task graph (P0)

| Task id | Agent | Input | Expected output (from example, productized) |
| --- | --- | --- | --- |
| `research_candidates_task` | researcher | `{job_requirements}` (+ optional candidate pack) | Up to **10** candidates with contact **if provided or publicly cited**, else “unknown — verify” + brief suitability |
| `evaluate_candidates_task` | evaluator | Job requirements + research output | Per-candidate advisory scores, strengths, gaps, and evidence-based rationale |
| `recommend_candidates_task` | recommender | Research and evaluation outputs | Ranked recruiter markdown report with draft-only outreach templates |

Kickoff input **must** be JSON-compatible:

```
{
  "job_requirements": "<required non-empty string>",
  "candidate_profiles": "<optional free text; omit or empty if unused>"
}
```

Chat MVP: map the user message to `job_requirements`. If the operator pastes synthetic profiles in the same message, the backend MAY split on a documented delimiter **or** place the full message in `job_requirements` and leave `candidate_profiles` empty — SAD picks one parse rule. **No CSV upload in MVP.** When `candidate_profiles` is empty and web research is off, the backend **injects the bundled fixture pack** (P0-5).

### Integration Requirements

| Integration | MVP | Deferred |
| --- | --- | --- |
| LLM API (`OPENAI_API_KEY`, default model `gpt-4o`, override `OPENAI_MODEL`) | Required | — |
| Serper (or equivalent search) | Opt-in only (`SERPER_API_KEY` + `AAMAD_ENABLE_WEB_RESEARCH=true`); default **off** | — |
| Chat API (AAMAD FE↔BE) | Required | — |
| ATS | No | P2 |
| Email/calendar send | No | P2 |
| LinkedIn official API | No | P2 |
| Vector resume / job-URL fit (`template_job_fit_assessment`) | No | P2 |

**Storage MVP:** In-memory or ephemeral job result for the **chat session only**. Discard request/response bodies at session end. Redacted traces may be kept ≤ **24 hours** under `project-context/2.build/logs` for debugging, then deleted. **No production candidate database. No real PII in the first environment.**

**AuthN/Z MVP:** Local/dev single-user; no SSO. Do not commit secrets (`.env.example` names only).

**Performance (MVP targets):** See NFR. One concurrent kickoff is acceptable; queue or reject additional.

### Infrastructure Specifications

- Hosting: local Docker/compose or single process (SAD/Deliver).
- Compute: developer laptop / small VM; LLM is external.
- Network: egress to LLM and optional search only.
- Monitoring: health endpoint; duration; error class; **no raw resumes in logs**.

---

## 11. Functional Requirements

### Core Features (Priority P0)

**P0-1 Job-requirements kickoff**  
*As a recruiter, I want to submit job requirements in the chat UI so that the crew can run.*  
**Acceptance criteria (AC-P0-1):**

- Chat accepts a non-empty `job_requirements` string (free text).
- Empty/whitespace-only `job_requirements` is rejected with a user-visible error (no crew start).
- Backend maps to `crew.kickoff(inputs={"job_requirements": ..., "candidate_profiles": ...})` with `candidate_profiles` defaulting to `""`.
- Optional `candidate_profiles` is free text only (synthetic/fixture content in the first environment).

**P0-2 Sequential three-agent run**  
*As a recruiter, I want research, scoring, outreach drafts, and a combined report so that I do not stitch tools myself.*  
**AC-P0-2:**

- Researcher, Evaluator, and Recommender agents/tasks exist in YAML.
- Process is sequential; Evaluator receives Researcher output, and Recommender receives research and evaluation outputs.
- Recommender supplies ranked recommendations, draft-only outreach, and the combined report.
- `allow_delegation=false` on all agents.
- Run completes or fails with a Diagnostic-style error in chat. **Hard cap:** `max_execution_time = 480` seconds.

**P0-3 Recruiter report**  
*As a recruiter, I want a markdown report of recommended candidates with scores and outreach strategy so that I can brief a hiring manager.*  
**AC-P0-3:**

- Final assistant message contains the recommender markdown (profiles, scores, outreach), not a raw stack trace on success.
- Report does not include a fenced copy of the entire job spec as required by the example (“no need to include the job requirements formatted as markdown without '```'”).
- UI marks the experience as **advisory / human review required**.

**P0-4 Safe sourcing policy**  
*As an operator, I need the product not to use LinkedIn cookie scraping so that we do not violate ToS or ban accounts.*  
**AC-P0-4:**

- Shipped code and docs **must not** instruct users to copy `li_at` or run the example LinkedIn Selenium tool.
- Researcher and Evaluator instructions retain the constraint against LinkedIn scraping.
- QA includes a check that the LinkedIn cookie tool is absent from the MVP tool bind list.

**P0-5 Fixture / demo path**  
*As a QA engineer / recruiter in a demo, I want a deterministic candidate set so that we can test without live search.*  
**AC-P0-5:**

- Documented fixture pack is injected when `candidate_profiles` is empty and web research is off, producing a report without Serper.
- Unit tests run without network to LinkedIn or Serper.

**P0-6 Secrets hygiene**  
*As an operator, I want keys only in environment variables.*  
**AC-P0-6:** `.env.example` lists `OPENAI_API_KEY`, optional `OPENAI_MODEL` (default `gpt-4o`), optional `SERPER_API_KEY`, optional `AAMAD_ENABLE_WEB_RESEARCH`; no secret values in artifacts or Prompt Trace.

**P0-7 Error and halt**  
*As a recruiter, I want a clear failure if the LLM or crew errors.*  
**AC-P0-7:** Chat shows a non-empty error state; no partial “fake candidates” presented as verified contacts without a “unverified” label (policy in reporter prompt / guardrail).

### Enhanced Features (Priority P1)

- File upload of profiles (still synthetic in demo env); MVP remains paste/`candidate_profiles` string.
- Progress events (task started/completed) in chat.
- Download report as `.md`.
- Operator-enabled Serper-backed research (`AAMAD_ENABLE_WEB_RESEARCH=true`) using **synthetic or public non-LinkedIn sources only**.

### Future Features (Priority P2 / Future Work)

- Job-fit slice: job URL + resume PDF (CrewAI `template_job_fit_assessment`) as a **separate** kickoff type.
- ATS push/pull (no preferred vendor).
- Official LinkedIn / job-board APIs.
- Send email/InMail via user OAuth (still HITL confirm).
- Interview scheduling.
- Bias-audit export, NYC notice workflow, DPIA templates.
- Candidate portal, SSO, multi-tenant.
- Internal talent marketplace matching (SHRM trend).
- Hierarchical manager process.
- Persistent candidate CRM.
- CSV profile ingest.

---

## 12. Non-Functional Requirements

### Performance

| Metric | MVP target |
| --- | --- |
| Time to first byte / chat ack | < 3s after submit |
| End-to-end kickoff (4 agents, fixture, no web) | **≤ 480 seconds** (`max_execution_time`); fail with timeout error if exceeded |
| Concurrent kickoffs | 1 (queue or 429) |
| Availability | Dev/demo; no 99.9% SLA |

### Security & Compliance

- Treat candidate names, emails, phones, unredacted resumes as **PII**.
- Human-in-the-loop: product is **decision support**, not sole automated hiring (GDPR Art. 22; EU AI Act high-risk employment AI).
- No production AEDT use (NYC LL144 and similar) — **out of MVP and out of this program’s production scope**.
- `security.require_security_assessment: true` → `@security.eng` before Deliver.
- Least-privilege tools; no shell as a recruiter tool.
- Redact secrets and PII from traces under `project-context/2.build/logs`.

### Scalability & Reliability

- Scale-out deferred; vertical/LLM rate limits first.
- On provider failure: fail the job, surface error, do not retry unbounded (adapter retry limit).
- Cancellation: if FE supports stop, backend should abort kickoff where the runtime allows (SAD).

---

## 13. User Experience Design

### Interface Requirements

- **Platform:** Web chat MVP (AAMAD frontend epic); desktop-first; mobile usable but not a separate app.
- **Theme:** `system` / `minimal` per `aamad.config.example.yml` (`prefer_modals: false`).
- **A11y:** Keyboard-submittable composer; readable contrast; errors in text not color-only (target WCAG 2.2 AA where the FE stack allows).
- **Copy:** Future Work labeled in UI for P1/P2 (AAMAD epics-index).

### Agent Interaction Design

- Recruiter speaks **job language**, not agent names (optional debug: show which task is running — P1).
- Feedback: streaming or “working” state during kickoff.
- Errors: actionable (missing key, timeout, validation).
- Explainability: scores **must** include justification text; unverified contact data labeled.

---

## 14. Success Metrics & KPIs

### Business / Operational

- Demo: **successful fixture kickoff** in QA (`qa.md`).
- Zero ToS incidents (no LinkedIn cookie feature).
- **No live-requisition success metric** in MVP (internal demo only).

### Technical

- Fixture kickoff success rate in CI: **100%** of mapped AC tests green for P0.
- Timeout/failure surfaced (not silent); 480s cap enforced.
- Cost: token usage logged per kickoff (no numeric $ target in MVP).

### User Experience

- Task completion: submit → report without operator CLI.
- Time-to-value: first report in one session.
- CSAT / accept-edit rate: **not instrumented in MVP** (manual QA observation only).

---

## 15. Implementation Strategy

### Development Phases

- **Phase 1 (Define):** This MRD + PRD; optional `*create-stories`; `@system.arch` SAD/SFS next.
- **Phase 2 (Build):** Setup → FE chat + BE crew → integration → QA (unit + integration mapped to AC-P0-*) → security.md.
- **Phase 3 (Deliver):** deploy.md + user-guide (`documentation.require_user_guide: true` in example config).

### Resource Requirements

- Personas per AAMAD; Python primary language (example config).
- LLM budget for QA runs.

### Risk Mitigation

| Risk | PRD control |
| --- | --- |
| LinkedIn scrape | P0-4 |
| Hallucinated contacts | P0-7 unlabeled contacts forbidden |
| Compliance overreach | MVP labeled advisory; P2 legal pack |
| Scope creep | P1/P2 lists; no ATS in MVP |
| Config missing at first authoring | Honor example YAML; **copy to `aamad.config.yml` as-is** (MRD-Q1) |

---

## 16. Launch & Go-to-Market Strategy

**N/A for MVP** (internal/operational AAMAD-generated application). No pricing, sales motion, or public launch. Commercialization, DPIA, AI Act deployer duties, and LL144 are **out of this program** unless the operator opens a new Define cycle.

---

## Quality Assurance Checklist

- [x] Requirements traceable to MRD, official CrewAI recruitment example, or recorded Assumptions
- [x] Technical specifications feasible with CrewAI adapter (YAML crew, sequential, HITL)
- [x] Success metrics aligned with time-to-shortlist and safe-use objectives
- [x] MVP vs Future Work boundaries explicit (P0 / P1 / P2)
- [x] Market sections included (MRD not skipped); GTM marked N/A for internal MVP

---

## Sources

1. `project-context/1.define/mrd.md` (create-mrd, 2026-09-30).
2. CrewAI-examples recruitment `agents.yaml`, `tasks.yaml`, `crew.py`, README — https://github.com/crewAIInc/crewAI-examples/tree/main/crews/recruitment (retrieved 2026-09-30).
3. `.cursor/templates/prd-template.md`, `.cursor/agents/product-mgr.md`, `.cursor/rules/adapter-crewai.mdc`, `aamad.config.example.yml`.
4. Operator request: recruitment assistant based on CrewAI recruitment example; `*create-mrd` then `*create-prd` (2026-09-30); follow-up to close Open Questions by PM judgment (2026-09-30).
5. SHRM / LinkedIn / EU AI Act / NYC LL144 citations as listed in MRD Sources (not repeated in full).

---

## Assumptions

- Elicitation (`*elicit-requirements`) was **not** run; system description inferred from the CrewAI example + operator use case.
- `aamad.config.yml` absent; preferences taken from `aamad.config.example.yml` (Python, crewai, minimal UI, security assessment required, unit+integration tests, user guide).
- `AAMAD_TARGET_RUNTIME` unset → **`crewai`**.
- First ship is **chat MVP + crew**, not a multi-tenant SaaS.
- “10 candidates” remains the research-task cap unless architecture documents a different N.
- Contact information in research output is **best-effort and must be verified by the recruiter**.
- Launch/GTM skipped as N/A (internal MVP); MRD still produced because the category is commercial TA software and the operator requested MRD.
- Example GPT-4o default may be replaced by an org model; quality of scoring will vary (not a P0 model pin beyond “LLM from env”).

---

## Open Questions

Resolved by PM judgment on 2026-09-30. No open questions remain for this Define phase.

| ID | Decision | Rationale |
| --- | --- | --- |
| PRD-Q1 | Create `aamad.config.yml` as a verbatim copy of `aamad.config.example.yml` with no preference deviations. | This preserves the AAMAD baseline and the default CrewAI architecture without adding product drift. |
| PRD-Q2 | First environment uses synthetic or fixture candidates only; no real candidate PII or live resumes are allowed in the MVP environment. | Legal and operational risk is lower, and the product remains a safe internal demo. |
| PRD-Q3 | Serper/web research stays off by default and is enabled only when the operator explicitly sets the API key and feature flag. | The default path should be deterministic and CI-safe; public sourcing is optional, not mandatory. |
| PRD-Q4 | Kickoff schema is a JSON-style payload with required `job_requirements` and optional `candidate_profiles` string fields. | This preserves the example contract while remaining simple for a chat MVP. |
| PRD-Q5 | Use `max_execution_time = 480` seconds and `max_rpm = 10` as the default operational caps. | These values align with the example constraints and keep runtime cost under control. |
| PRD-Q6 | The P1 job-fit PDF workflow is deferred to P2 and is not part of the same release train. | The first release is a recruiter-reporting assistant, not a full document-processing product. |
| PRD-Q7 | No production hiring use is approved in the EU, UK, or NYC for this program. The product remains internal/demo only until counsel and governance review. | The MRD already defines the legal boundary and the product must stay human reviewed. |
| PRD-Q8 | The “accept/edit” KPI is not instrumented in MVP; manual QA observation is the method for this release. | This avoids building measurement infrastructure before the product is stabilized. |
| PRD-Q9 | Use three agents: Researcher, Evaluator, and Recommender. Recommender combines outreach drafting and report compilation. | This aligns the PRD with the implemented runtime and SAD while preserving the user-visible workflow and all required outputs. |

---

## Audit

- **Timestamp:** 2026-09-30T18:25:00-03:00
- **Persona id:** `product-mgr`
- **Action:** `create-prd`
- **Resolved `AAMAD_TARGET_RUNTIME`:** `crewai` (unset; adapter-registry default; `aamad.config.example.yml` `runtime.target: crewai`)
- **Warning:** `aamad.config.yml` missing at authoring time.
- **Prompt Trace:** Omitted; PRD authored from MRD + official example files (Sources). No production user prompts captured.
- **Model / tools:** Cursor Grok 4.6; no application code; no SAD/SFS/Build artifacts modified.
- **Temperature / max_tokens:** n/a (interactive Define-phase authoring).
- **Preceding action:** `create-mrd` → `project-context/1.define/mrd.md`.
- **Follow-up:** Synchronized the PRD agent count and task graph with the authoritative three-agent SAD/runtime on 2026-10-02.
