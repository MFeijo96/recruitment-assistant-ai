# Market Research Document: Recruitment Assistant (Multi-Agent)

## Research Query Structure

**Primary Focus**: Multi-agent recruitment assistant that research-sources, scores, drafts outreach, and reports a recruiter-ready shortlist from a job specification — productized from the CrewAI “AI Crew for Recruitment” example.

**Selected Runtime** (implementation choice for the generated MVP; not the AAMAD methodology): `crewai` (resolved default; `AAMAD_TARGET_RUNTIME` unset; `aamad.config.yml` not present; `aamad.config.example.yml` sets `runtime.target: crewai`).

**System concept under research**: Recruiter-operated chat MVP in which a sequential crew (researcher → evaluator → recommender) produces an explainable candidate report and draft-only outreach. Human review remains mandatory; the product does not auto-hire or auto-send outreach. The recommender combines the reporting and outreach roles in the official four-agent reference example.

---

## Executive Summary

**Market Opportunity.** Hiring remains operationally expensive and slow. SHRM’s 2025 Talent Trends work finds **69% of organizations still struggle to fill full-time roles**, with too few applicants, competitor poaching, and candidate ghosting as leading frictions. SHRM’s 2025 recruiting benchmarking brief places **median time-to-fill at roughly 1.5 months**. The broader recruitment-software market is estimated at about **USD 2.54B in 2025 / USD 2.78B in 2026** (The Business Research Company, via GII) versus **USD 3.61B (2025) / USD 3.77B (2026)** (Mordor Intelligence) — a material spread that must be treated as range, not a single TAM. Dedicated **AI recruitment** software is smaller: Mordor **USD 596M (2025) → USD 641M (2026) → USD 921M (2031) at 7.52% CAGR**; Research Nester **USD 708M (2025) / USD 752M (2026)**; Market Research Future **USD 638M–USD 660M (2025)** depending on the published table. Cloud ATS suites and generative copilots (iCIMS, Workday, Greenhouse, LinkedIn Hiring Assistant) are the incumbent spend; the gap this product targets is **explainable, role-scoped multi-agent screening for teams that cannot or will not buy an enterprise ATS AI module**.

**Technical Feasibility.** The official CrewAI recruitment example already implements the four-agent sequential pattern (`researcher`, `matcher`, `communicator`, `reporter`) with YAML agent/task config, `Process.sequential`, Serper/ScrapeWebsite tools, and a reporter task that merges prior outputs. That pattern maps cleanly to AAMAD’s CrewAI adapter (YAML-first agents/tasks, `allow_delegation=false`, explicit `Task.context`). Feasibility is **high for an MVP chat kickoff** that takes `{job_requirements}` (and optional operator-supplied candidate profiles) and returns a markdown report. Feasibility is **low for production LinkedIn cookie/Selenium sourcing**: the example README states that cookie auth is demonstration-only and **may violate LinkedIn terms of service**. EU AI Act Annex III and GDPR treat candidate screening/ranking as high-risk processing even when a human makes the final hire; NYC Local Law 144 adds bias-audit and notice duties if the tool is used as an AEDT for NYC candidates. Those constraints must shape architecture (human-in-the-loop, evidence citations, no sole automated hiring) more than they block an MVP.

**Recommended Approach.** Position the MVP as an **internal recruiter copilot**, not a replacement ATS: sequential CrewAI crew, least-privilege web search (or fixture data) instead of LinkedIn scraping, structured scores with written justifications, draft outreach **templates only** (no send), and a chat UI for kickoff plus report display. Go to market later as a commercial add-on only after bias, retention, and ATS-integration work. Immediate next step is a PRD that freezes this scope and defers ATS, CRM, and official talent-network APIs.

---

## Problem Statement

The recruitment assistant solves a core operational problem in talent acquisition: recruiters and hiring teams must manually source, review, compare, and prioritize candidates across fragmented systems, often with inconsistent methods and limited visibility into why one candidate is stronger than another. In practice, this creates long hiring cycles, uneven decision quality, and heavy context switching across job descriptions, resume reviews, public search, email, and ATS tools.

Manual candidate sourcing and evaluation are inefficient because they depend on repetitive work that is hard to scale: finding candidates, validating their fit, comparing competing profiles, and drafting outreach are all time-heavy tasks. When teams try to do these steps manually, candidate quality varies, hiring managers receive inconsistent recommendations, and the recruiter often spends too much time on lower-value tasks instead of candidate relationship management and final hiring decisions.

## Target Users

**Primary users**
- Recruiters and TA coordinators who need to source, screen, and prioritize candidates for a requisition.
- Hiring managers who need a structured shortlist and recommendation summary before interviews.
- HR teams managing high-volume or multi-role hiring cycles that require repeatable evaluation and reporting.

**Secondary users**
- Internal staffing teams and operations teams that want a faster, more consistent shortlist generation process.
- Product operators / demo users who need a safe, explainable AI assistant for recruitment workflows without exposing live candidate PII.

## Market Opportunity

The market opportunity is driven by a combination of labor-market pressure and operational inefficiency. Recruiters still face slow hiring cycles, high volume of candidate review, and the need to reduce time-to-fill without sacrificing quality. The product creates value by reducing sourcing time, improving fit assessment consistency, and scaling outreach planning for higher-volume recruitment activity.

Key opportunities include:
- Time savings in candidate sourcing and comparison
- Improved matching accuracy through structured scoring and written justifications
- Scalability for repeated hiring workflows across multiple roles or hiring managers
- Better explainability than a black-box AI screening tool
- Reduced reliance on manual spreadsheet and search-heavy workflows

## Competitive Landscape

The recruitment market is dominated by established ATS platforms, manual recruiting workflows, and specialized sourcing or assessment tools. Common alternatives include Greenhouse, Lever, Workday Recruiting, iCIMS, and LinkedIn Recruiter/Hiring Assistant. These platforms provide strong workflow coverage, but they are often tied to system-of-record processes, expensive enterprise pricing, or network-specific tooling.

Manual recruitment remains widespread and is still highly inefficient: recruiters often gather information from multiple websites, compare resume details line-by-line, and prepare briefings in ad hoc formats. This process is slow and difficult to scale when multiple requisitions or hiring managers are involved.

An AI-powered multi-agent system differs from these incumbents in three important ways. First, it decomposes the recruitment workflow into specialized roles (research, match, communications, and reporting) rather than treating candidate evaluation as a single opaque action. Second, it produces transparent outputs such as scores, rationale, and outreach drafts that recruiters can review before acting. Third, it is designed as a lightweight, explainable copilot that can complement existing ATS workflows rather than replacing them outright.

---

## Detailed Findings by Dimension

### 1. Market Analysis & Opportunity Assessment

**Key Insights**

1. **Recruiting demand is still elevated.** SHRM (2025) reports **69%** of organizations challenged filling full-time jobs (down from 77% the prior year and 91% in 2022, but still near 2016 levels). Skill shortages and ghosting keep recruiter workload high even as the “everything is vacant” peak recedes.
2. **Time and cost, not “more resumes,” are the buyer pain.** SHRM 2025 benchmarking: median time-to-fill ~**1.5 months**; screening and interviewing each on the order of **8–9 days**. Cost-per-hire has risen even where executive time-to-fill improved — buyers will pay for cycle-time reduction with quality, not raw volume.
3. **AI in HR is crossing from experiment to default, but depth is uneven.** SHRM: **43%** of organizations use AI for HR in 2025 (up from **26%** in 2024); **~90%** of users report time or efficiency gains; recruiting (JD generation, resume screen, search) is the primary use. LinkedIn Future of Recruiting 2025: **37%** of TA pros experimenting or integrating generative AI (from **27%**), reporting **~20% of the workweek saved** (~one day/week); **73%** believe AI will change hiring. Mordor’s AI-recruitment note cites **70% experimenting / 92% claiming benefits** — treat as a third, vendor-adjacent datapoint that **conflicts** with SHRM/LinkedIn magnitudes.
4. **Incumbents occupy workflow, not “agent crews.”** Greenhouse (structured hiring + governed AI), Lever (ATS+CRM), Workday Recruiting / HiredScore (enterprise HCM), iCIMS copilots, LinkedIn Recruiter + Hiring Assistant (network-native sourcing; Sprad cites GA Sep 2025 English and vendor claims of 1.5–4+ hours saved per role and ~$450M annualized HA revenue), HireEZ/SeekOut/Gem/Juicebox (sourcing), HireVue (assessment), Paradox (conversational high-volume). Feature gap: **transparent multi-step agent traces** (research → score → outreach draft → recruiter report) that a small team can run without an ATS seat.
5. **Willingness to pay is software-subscription, not one-off reports.** Recruitment software is cloud-heavy (~70% of spend per Mordor). SMB/startup TA teams already buy LinkedIn Recruiter and a lightweight ATS; they will trial a copilot if it **does not require cookie scraping or a new system of record**.

**Data Points**

| Claim | Figure | Source |
| --- | --- | --- |
| Full-time recruiting difficulty | 69% of orgs (2025) | SHRM Talent Trends 2025 |
| AI for HR tasks | 43% (2025) vs 26% (2024) | SHRM Talent Trends 2025 |
| Users reporting time/efficiency gain | ~90% of AI-using orgs | SHRM / SHRM MENA summary 2025 |
| GenAI in TA | 37% experiment/integrate; +20% week saved | LinkedIn Future of Recruiting 2025 |
| Median time-to-fill | ~1.5 months | SHRM 2025 Recruiting Executives Benchmarking |
| Recruitment software (TBRC) | USD 2.54B (2025) → 2.78B (2026) → 4.05B (2030); CAGR ~9.5–9.9% | TBRC via GII, 2026 report page |
| Recruitment software (Mordor) | USD 3.61B (2025), 3.77B (2026), 5.5B (2031); CAGR 7.85% 2026–31 | Mordor Intelligence |
| AI recruitment (Mordor) | USD 596M (2025), 641M (2026), 921M (2031); 7.52% CAGR | Mordor Intelligence |
| AI recruitment (Research Nester) | USD 708M (2025), 752M (2026), 1.39B (2035); ~7% CAGR | Research Nester, published 13 Oct 2025 |
| AI recruitment (MRFR) | ~USD 638M (2025 listed) / 660M (2025 alt); ~USD 1.29–1.38B by 2035 | Market Research Future |
| Cloud share of recruitment software | ~70% | Mordor recruitment software report |
| North America share (AI recruitment) | ~38–39% | Research Nester; MRFR |

**Source Citations.** SHRM Talent Trends 2025; SHRM State of Recruiting 2025 briefing; LinkedIn Future of Recruiting 2025; Mordor recruitment software and AI recruitment reports (accessed Sep 2026); TBRC/GII Recruitment Software Global Market Report 2026; Research Nester AI Recruitment (Oct 2025); Market Research Future AI Recruitment; Greenhouse “best recruiting tools 2026”; Juicebox recruiting software roundup 2026; Sprad AI sourcing vs LinkedIn Recruiter (Hiring Assistant GA).

**Implications.** TAM for “all recruitment software” is **not** the addressable market for this MVP. SAM is **AI-assisted screening/sourcing copilots** (hundreds of millions USD, not billions). Beachhead: technical recruiting teams and AAMAD/CrewAI adopters who already accept chat-based agent UIs. Do not compete with Workday or LinkedIn Recruiter on pipeline-of-record; **complement** them with an explainable shortlist artifact.

**Conflicting information.** Market-size publishers disagree by **~USD 1B+** on “recruitment software” and by **~USD 100M** on “AI recruitment.” SHRM AI-in-HR (43%) vs LinkedIn GenAI-in-TA (37%) vs Mordor “70% experimenting” are **different questions**; prefer SHRM/LinkedIn for product narrative and footnote Mordor as broader “AI in HR experiment” language.

---

### 2. Technical Feasibility & Requirements Analysis

**Key Insights**

1. **Reference architecture exists.** CrewAI-examples `crews/recruitment`: four agents, four tasks, sequential process, reporter `context` from research/match/outreach, tools SerperDevTool + ScrapeWebsiteTool + optional LinkedInTool. AAMAD CrewAI adapter requires the same YAML-first layout, `max_iter <= 12` unless justified, `memory=False` default, `allow_delegation=false`.
2. **LinkedIn cookie tool is a hard product/legal no for production.** Official README (João Moura / crewAIInc): cookies for Selenium LinkedIn demo **may ban accounts**; authors **do not endorse real-world use**. Matcher task already says “Don't try to scrape people's linkedin, since you don't have access to it.” MVP sourcing must be **job_requirements + operator-pasted/uploaded profiles and/or licensed search APIs**, with a **fixture corpus** for tests.
3. **Runtime adapter fit.** `crewai` is the best fit for this use case (declarative task graph). `claude-agent-sdk` and `cursor-sdk` could host equivalent roles but would remap YAML to AgentDefinition / TypeScript contracts; product scope should stay runtime-agnostic while **Build defaults to crewai**.
4. **Integrations for production vs MVP.** Production wish-list: ATS APIs (Greenhouse, Lever, Workday), official LinkedIn Recruiter / Jobs APIs, calendar (scheduling — **out of example scope**), email send. MVP: LLM provider key, optional Serper (or disabled tools + fixtures), no ATS, no mail send.
5. **Scalability bottleneck is LLM turns, not HTTP.** One kickoff ≈ four sequential agent runs with tool loops. Concurrency = number of simultaneous recruiter jobs. Cost risk is token/tool spend per requisition, not users. Cap `max_rpm`, `max_execution_time`, and persist traces under `project-context/2.build/logs` (redacted).

**Data Points**

- Example default model: **GPT-4o** (README; cost warning).
- Example output contract: **10 candidate profiles** (research task); ranked scores + justifications (matcher); outreach templates (communicator); markdown recruiter report (reporter).
- CrewAI sequential process: tasks in list order; `Task.context` for merge (CrewAI docs, sequential process / processes).
- Related CrewAI assets: `template_job_fit_assessment` (job URL + resume PDF → fit report; Firecrawl + PyMuPDF) — useful **P1** pattern for resume-vs-JD, not the primary example’s sourcing crew.

**Technical Risks**

| Risk | Mitigation |
| --- | --- |
| Hallucinated candidates/contact data | Require citations; fixture mode; recruiter confirmation before any outreach |
| Tool/ToS violations | Ban cookie LinkedIn scrape; document allowed tools |
| Bias / disparate impact | Human override; no auto-reject; defer production AEDT use until audit plan exists |
| Cost overrun | RPM/time/iter caps; cheaper model option in Assumptions |
| Context overflow on long reports | Structured sections; cap candidate N (10) |

**Infrastructure.** MVP: single backend process + chat UI (AAMAD frontend epic), local or one small VM/container. Secrets: `OPENAI_API_KEY` (or org LLM gateway), optional `SERPER_API_KEY`. No candidate PII in git.

**Implications.** Architecture should copy **roles and task graph** from the example, not its LinkedIn tool. SAD must treat the reporter markdown as the API response body for the chat MVP.

---

### 3. User Experience & Workflow Analysis

**Key Insights**

1. **Primary persona: recruiter / TA coordinator** running a single requisition. Secondary: hiring manager who **reads** the report (P1: share link). Not in MVP: candidate-facing portal.
2. **Journey (target).** Recruiter pastes job requirements → optional candidate list or “research public sources” → waits with progress/status → receives ranked report (profiles, scores, evidence, outreach drafts) → edits/approves → copies outreach **manually**. Human oversight at score acceptance (SHRM: AI helps early funnel; humans still own relationships — LinkedIn: relationship-building skill demand up sharply).
3. **UI.** AAMAD MVP chat (minimal theme per example config). Show: job input, run status, final markdown, error/halt diagnostic. Future: table of scores, download, ATS push.
4. **Automation vs HITL.** Fully automate: research compilation, scoring draft, template generation, report assembly. Never automate: offer/reject decisions, live InMail/email send, LinkedIn login.
5. **Adoption barriers.** Trust (black-box scores), legal fear (AI Act / LL144), garbage-in job specs, incumbent ATS already “good enough.” Enablers: citations, fixture demo, 20% time-save narrative (LinkedIn), SHRM ~90% efficiency among AI users.

**Success Metrics (research-backed, productized in PRD)**

- Recruiter time on first shortlist vs baseline (directional target: reclaim a portion of the **~20% week** LinkedIn reports for GenAI users).
- % of report recommendations **accepted or edited** (not discarded).
- Task completion: kickoff → report without fatal error.
- Zero production sends without human click (policy KPI).

**Implications.** Chat is sufficient for MVP; structured scorecards are P1. Transparency of **why this score** is a P0 UX requirement, not polish.

---

### 4. Production & Operations Requirements

**Key Insights**

1. **Deploy.** Smallest MVP: compose or single service matching AAMAD Deliver (after QA + security.md because example config sets `security.require_security_assessment: true`). Health check on API; env-only secrets.
2. **Observability.** Prompt Trace, task start/stop, tool names (not payloads with PII), token/cost, duration. Redact emails/phones in logs.
3. **Security & compliance.** Candidate data = personal data (GDPR if EU data subjects). Screening/ranking ≈ **high-risk AI** (EU AI Act Annex III employment; Ogletree, Eversheds). GDPR DPIA typically required; Article 22 if solely automated significant decisions — **product must not be solely automated**. NYC LL144: bias audit + public summary + **10 business days’ notice** if used as AEDT for NYC. EEOC Title VII / 80% rule still applies independently of NYC. Colorado AI Act / Illinois HB 3773 (2026) expand US state duties — **Future Work** for multi-state launch.
4. **Maintenance.** YAML agent/task versioning; pin CrewAI; model swap recorded in Audit. Fixture tests must not call LinkedIn.
5. **Cost structure.** Dominant opex: LLM + optional Serper. Dev cost is AAMAD Phase 2 crew (FE/BE/integration/QA/security). No multi-region HA in MVP.
6. **Business continuity.** If LLM provider is down, fail with Diagnostic; do not silently skip scoring.

**Implications.** Legal is a **go/no-go for production hiring use**, not for an internal demo MVP labeled “decision support / human review required.” Commercial launch needs counsel + DPIA + (if NYC) audit vendor.

---

### 5. Innovation & Differentiation Analysis

**Key Insights**

1. **UVP.** Role-playing sequential crew with **auditable task artifacts** vs a single “AI screen this resume” button inside an ATS. Matches how recruiters already decompose work (source → score → message → brief the HM).
2. **Emerging tech.** Skills ontologies, embeddings pre-filter (seen in community CrewAI recruiters), official Recruiter APIs, Hiring Assistant inside LinkedIn — **do not scrape to compete**.
3. **Patent landscape.** Not researched at claim level. **Decision:** proceed with MVP on MIT example + Apache-2.0 AAMAD licenses; commercial FTO is deferred to legal review before any paid launch (not a Build blocker).
4. **Trends.** Explainable AI dashboards (Mordor: EU AI Act steering vendors); skills-based hiring; internal talent marketplaces (SHRM 35% in 2025 vs 25% in 2024) — internal mobility is a **P2** adjacent product.
5. **Partnerships.** Serper/search; later Greenhouse/Lever OAuth; LLM gateway. Not LinkedIn unofficial.
6. **Monetization.** MVP: internal/operational tool (seat-time savings). Later: per-requisition or per-recruiter SaaS **below** Recruiter sitelicense, sold as copilot.

**Implications.** Differentiate on **trace + templates + recruiter report**, not on “we have more profiles than LinkedIn.”

---

## Critical Decision Points

### Go / No-Go Factors

| Factor | Gate |
| --- | --- |
| Recruiter can complete job_requirements → report in one chat session | Go for MVP |
| No LinkedIn cookie/Selenium in shipped product | Go |
| Human must confirm before any external candidate contact | Go |
| Production use as unsupervised hiring filter in EU/NYC | **No-go** until compliance package |
| Claiming statistically validated “best candidate” | **No-go** (example is heuristic LLM scoring) |

### Technical Architecture Choices

- **Runtime:** `crewai` sequential, YAML agents/tasks, `allow_delegation=false`, `memory=false`.
- **Tools MVP:** none or Serper + scrape of **operator-approved public URLs**; fixture candidate set for CI.
- **Interface:** AAMAD chat MVP; report as markdown (example reporter contract: markdown without code fences).
- **Defer:** hierarchical manager, ATS, send-email, scheduling, PDF resume pipeline (job-fit template is a later epic).

### Market Positioning

- **MVP:** Internal recruitment assistant / demo of CrewAI recruitment pattern with a safe tool policy.
- **Later commercial:** “Explainable multi-agent shortlist copilot for TA teams on lightweight ATS stacks,” not “AI ATS.”

### Resource Requirements

- Define: this MRD + PRD (and recommended stories).
- Build: AAMAD Phase 2 personas; Python + CrewAI per example config language.
- Timeline: MVP in one AAMAD build cycle; compliance and ATS in 6–12 months.
- Budget: LLM spend per demo run (GPT-4o-class) plus optional search API; no enterprise sales motion in MVP.

---

## Risk Assessment Matrix

### High Risk

- **ToS / unauthorized access** if LinkedIn cookie scraping ships.
- **Unlawful automated employment decisions** (GDPR Art. 22, AI Act high-risk duties, NYC AEDT) if scores auto-reject.
- **PII leakage** in Prompt Trace, git, or logs.
- **Hallucinated people and contact details** leading to brand/legal harm.

### Medium Risk

- **Bias** in LLM matching (education/name proxies).
- **Market-size overclaim** in sales (publisher disagreement).
- **Cost** of four sequential GPT-4o agents with web tools.
- **Incumbent bundling** (Greenhouse AI, LinkedIn Hiring Assistant) reducing willingness to add another tool.

### Low Risk

- Chat UI sufficiency for MVP (recruiters already live in chat/email).
- Sequential vs hierarchical process (example already sequential).
- Theme/visual style (minimal/system per example config).

---

## Actionable Recommendations

### Immediate (48 hours)

1. Freeze MVP: four example agents, sequential tasks, chat kickoff, **no LinkedIn cookies**.
2. Author PRD with P0/P1/P2 and acceptance criteria; record runtime `crewai`.
3. Copy `aamad.config.example.yml` → `aamad.config.yml` **as-is** (resolved 2026-09-30: Python, CrewAI, minimal UI, security assessment required).

### Short-term (30 days)

1. `@system.arch` SAD/SFS; then `@project.mgr` setup; FE/BE/integration/QA/security.
2. Fixture dataset + unit tests mapped to AC IDs (`testing.map_to_acceptance_criteria: true` in example config).
3. Security assessment before Deliver (`require_security_assessment: true`).

### Long-term (6–12 months)

1. Official sourcing APIs / ATS connectors; bias-audit process if used as AEDT.
2. Resume PDF job-fit path (CrewAI job-fit template pattern).
3. Internal mobility / talent-marketplace adjacent workflow (SHRM trend).

---

## Sources

1. CrewAI Inc., `crewAI-examples/crews/recruitment` README, agents.yaml, tasks.yaml, crew.py — https://github.com/crewAIInc/crewAI-examples/tree/main/crews/recruitment (retrieved 2026-09-30).
2. CrewAI Inc., example disclaimer on LinkedIn cookies / Selenium (same README).
3. CrewAI sequential process documentation — https://docs.crewai.com/edge/en/learn/sequential-process (retrieved 2026-09-30).
4. CrewAI crews / processes — https://docs.crewai.com/edge/en/concepts/crews and https://docs.crewai.com/v1.15.9/en/concepts/processes (retrieved 2026-09-30).
5. CrewAI Inc., `template_job_fit_assessment` — https://github.com/crewAIInc/template_job_fit_assessment (retrieved 2026-09-30).
6. SHRM, 2025 Talent Trends — https://www.shrm.org/topics-tools/research/2025-talent-trends (retrieved 2026-09-30).
7. SHRM MENA, “Uncertain Economy Adds to Recruitment Challenges” (Talent Trends 2025) — https://www.shrm.org/mena/topics-tools/news/talent-acquisition/shrm-talent-trends-2025-recruitment-challenges (retrieved 2026-09-30).
8. SHRM Executive Network, “The State of Recruiting 2025” — https://www.shrm.org/executive-network/insights/people-strategy/state-of-recruiting-2025-insights-to-maximize-recruitment (retrieved 2026-09-30).
9. LinkedIn Talent, Future of Recruiting 2025 — https://business.linkedin.com/hire/resources/future-of-recruiting (retrieved 2026-09-30).
10. LinkedIn Talent Blog, “How AI Will Redefine Recruiting in 2025” — https://www.linkedin.com/business/talent/blog/talent-acquisition/future-of-recruiting-2025 (retrieved 2026-09-30).
11. The Business Research Company / GII, Recruitment Software Global Market Report 2026 — https://www.giiresearch.com/report/tbrc1977383-recruitment-software-global-market-report.html (retrieved 2026-09-30).
12. Mordor Intelligence, Recruitment Software Market — https://www.mordorintelligence.com/industry-reports/recruitment-software-market (retrieved 2026-09-30).
13. Mordor Intelligence, AI Recruitment Market — https://www.mordorintelligence.com/industry-reports/ai-recruitment-market (retrieved 2026-09-30).
14. Research Nester, AI Recruitment Market (published 2025-10-13) — https://www.researchnester.com/reports/ai-recruitment-market/6828 (retrieved 2026-09-30).
15. Market Research Future, AI Recruitment Market — https://www.marketresearchfuture.com/reports/ai-recruitment-market-8289 (retrieved 2026-09-30).
16. Greenhouse, “The top 10 best recruiting tools in 2026” — https://www.greenhouse.com/blog/best-recruiting-tools (retrieved 2026-09-30).
17. Juicebox, “14 Best recruiting software examples (in 2026)” — https://juicebox.ai/blog/recruiting-software-examples (retrieved 2026-09-30).
18. FuturePicker, Greenhouse vs Lever vs Workday vs HireEZ (2026) — https://futurepicker.com/en/ai-recruiting-tools-greenhouse-lever-workday-hireez-2026-en/ (retrieved 2026-09-30).
19. Sprad, “AI Sourcing vs LinkedIn Recruiter” (Hiring Assistant metrics; treat as secondary/vendor-adjacent) — https://sprad.io/blog/ai-sourcing-vs-linkedin-recruiter-where-time-actually-goes (retrieved 2026-09-30).
20. NYC DCWP, Automated Employment Decision Tools (Local Law 144) — https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page (retrieved 2026-09-30).
21. Seyfarth, NYC LL144 final rules (enforcement 5 Jul 2023) — https://www.seyfarth.com/news-insights/new-york-city-releases-final-rules-implementing-local-law-144-aimed-at-curbing-artificial-intelligence-bias-in-employment-decisions.html (retrieved 2026-09-30).
22. Ogletree, EU AI Act + GDPR for AI recruitment tools — https://ogletree.com/insights-resources/blog-posts/deployment-of-ai-recruitment-tools-in-the-eu-employer-obligations-under-gdpr-and-eu-ai-act/ (retrieved 2026-09-30).
23. Eversheds Sutherland, EU AI Act high-risk employment systems — https://www.eversheds-sutherland.com/en/global/insights/eu-ai-act-high-risk-ai-systems-in-employment (retrieved 2026-09-30).
24. Confir, GDPR and EU AI Act intersection (DPIA vs FRIA; Digital Omnibus dates as reported) — https://confir.eu/ai-governance/gdpr-ai-act-intersection (retrieved 2026-09-30).
25. AAMAD project: `README.md`, `.cursor/templates/mrd-template.md`, `.cursor/rules/adapter-crewai.mdc`, `aamad.config.example.yml` (workspace, 2026-09-30).
26. Stakeholder intent: operator request to base the product on the CrewAI recruitment example and to produce MRD then PRD (this session, 2026-09-30).

---

## Assumptions

- No `AAMAD_TARGET_RUNTIME` in the environment at first research time; runtime resolved to **`crewai`** per adapter registry default and example config. **MRD-Q1:** project config SHALL match `aamad.config.example.yml` verbatim.
- No `system-description.md` / elicitation questionnaire; use-case specified as CrewAI recruitment example + recruitment assistant application.
- Product is **market-researchable** (TA software category) even if first deployment is internal; MRD is therefore **not skipped**.
- The official example’s “10 candidates” cap is retained. Its four roles are reference material; the MVP uses the three-role workflow resolved in MRD-Q9 and the SAD.
- Market figures are **publisher estimates** (paywalled full methodologies); used as ranges.
- LinkedIn Hiring Assistant revenue/time-saved figures are **vendor-reported via secondary blogs** and are not independently audited.
- Digital Omnibus / Annex III application dates (e.g. Dec 2027) are cited from legal commentary and **must be verified by counsel**.
- Patent/FTO: no opinion issued; MVP proceeds on MIT example + Apache-2.0 AAMAD; commercial FTO before paid launch.
- **MRD-Q2–Q8:** see Resolved Product Decisions (internal demo, no live PII, opt-in Serper, gpt-4o, drafts-only send, no ATS, no production jurisdiction launch, job-fit P2).

---

## Resolved Product Decisions

Operator asked `@product-mgr` to answer remaining Open Questions by judgment (2026-09-30). Binding for PRD/SAD unless the operator overrides in writing.

| ID | Decision |
| --- | --- |
| MRD-Q1 | Copy `aamad.config.example.yml` → `aamad.config.yml` **with no preference changes** (Python, `runtime.target: crewai`, minimal/system UI, `require_security_assessment: true`, unit + integration tests, user guide). |
| MRD-Q2 | First deployment is an **internal demo / AAMAD MVP**, not live requisitions. **No real candidate PII** in the first environment; use fixtures or operator-authored synthetic profiles. |
| MRD-Q3 | Kickoff accepts **`job_requirements` (required)** and **`candidate_profiles` (optional free text)**. **No CSV parser in MVP.** Serper/web research is **opt-in** (API key + enable flag), **off by default** for demo/CI. |
| MRD-Q4 | LLM via **`OPENAI_API_KEY`**. Default model **`gpt-4o`** (official example). Override with `OPENAI_MODEL` if a gateway requires it. |
| MRD-Q5 | MVP outreach is **drafts only**. **Send-via-OAuth is P2**, not this release. |
| MRD-Q6 | **No ATS in use.** No vendor-specific connector. Generic ATS integration remains P2 with no preferred vendor. |
| MRD-Q7 | **No production hiring launch** in EU, UK, NYC, or other US states in this program. MVP is internal/demo. Still apply **HITL + no sole automated rejection**. NYC AEDT production use is out of scope. |
| MRD-Q8 | Job-fit PDF (`template_job_fit_assessment`) is a **separate product slice at P2**, not P1 and not the same MVP train. |
| MRD-Q9 | The MVP uses three sequential roles: Researcher, Evaluator, and Recommender. Recommender combines the reference example’s outreach-drafting and reporting responsibilities; the official example’s four-agent design remains research provenance, not the product contract. | This matches the SAD and running backend while retaining ranked assessments, outreach drafts, and the final report. |

---

## Open Questions

None remaining for `@product-mgr`. Counsel should still verify AI Act application dates cited in Sources (legal verification, not a product-scope gap). `@system.arch` may refine hosting topology but must not reopen the table above without an operator change.

---

## Audit

- **Timestamp:** 2026-09-30T18:15:00-03:00 (create-mrd); **2026-09-30T18:20:00-03:00** (resolve Open Questions by PM judgment)
- **Persona id:** `product-mgr`
- **Action:** `create-mrd` (updated in place to close Open Questions)
- **Resolved `AAMAD_TARGET_RUNTIME`:** `crewai` (unset in environment; default per adapter-registry; aligned with `aamad.config.example.yml` `runtime.target`)
- **Warning:** `aamad.config.yml` was missing at first authoring; **decision MRD-Q1** is to add it as a verbatim copy of the example (operator/setup may still perform the copy).
- **Prompt Trace:** Omitted from this artifact (contains no production prompts). Research queries and official example files are listed under Sources.
- **Model / tools:** Cursor Grok 4.6; WebSearch/WebFetch for market and example grounding; no application code written.
- **Temperature / max_tokens:** n/a (interactive Define-phase authoring).
