# Recruitment Assistant

## Project Title and Description

The Recruitment Assistant is an AI-powered multi-agent recruiting tool that helps recruiters source, evaluate, and prioritize candidates for a role using a structured, explainable workflow. The product accepts a job requirement, analyzes candidate fit, and produces a ranked shortlist with rationale for recruiter review.

This project is designed to reduce manual recruiting effort while keeping decision-making in human hands. It is intended to help recruiters find qualified candidates faster, compare them consistently, and prepare a stronger shortlist with less context switching and less spreadsheet-heavy work.

### Value proposition

- Faster candidate screening and shortlist creation
- More consistent candidate evaluation across roles
- Clear explanations behind recommended matches
- Reduced dependency on manual sourcing workflows
- Safe, human-reviewed recruiting support for an internal MVP

---

## Problem Statement

Recruiting teams still spend a large share of their time on repetitive work: sourcing candidates, reviewing profiles, comparing qualifications, and manually preparing shortlist recommendations. This process is slow, inconsistent, and difficult to scale when hiring demand increases or multiple hiring managers are involved.

Manual recruitment is especially inefficient because it relies on fragmented systems and repeated comparison work. Recruiters must often move between job descriptions, ATS data, public search, email, and individual candidate profiles to build a coherent recommendation. The result is slower hiring cycles, inconsistent candidate quality, and a heavier burden on recruiters.

This project solves that problem by using a structured multi-agent workflow to automate the most time-consuming parts of the screening and recommendation process while keeping recruiters in the decision loop.

---

## Features

### Core capabilities

- Candidate search based on job requirements
- Automated candidate evaluation against role criteria
- Ranked candidate recommendations with rationale
- Recruiter-ready markdown shortlist report
- Synthetic or fixture-based candidate data for safe demo usage
- Human-in-the-loop review before outreach or hiring decisions

### What users can expect

- A fast path from job brief to shortlist
- More transparent explanation of why a candidate is recommended
- Better decision support for recruiters and hiring managers
- Lower operational overhead compared with purely manual sourcing workflows

---

## Architecture Overview

The application has a React/Vite browser client and a FastAPI service. The API accepts a job brief, starts one in-memory run, and executes three CrewAI agents sequentially. The browser polls the run status and displays the completed advisory report.

```mermaid
flowchart LR
    A[React + Vite UI] -->|POST /api/runs| B[FastAPI]
    B --> C[In-memory run registry]
    C --> D[Researcher]
    D --> E[Evaluator]
    E --> F[Recommender]
    F -->|Report and status| B
    B -->|Poll /api/runs/{id}| A
    D -.->|Default| G[Synthetic fixtures]
    D -.->|Optional| H[Serper search]
    D --> I[LLM provider]
    E --> I
    F --> I
```

The Vite development server proxies `/api` and `/healthz` to FastAPI. CrewAI configuration lives in YAML, while Python builds and runs the sequential crew. When no candidate profiles are supplied and web research is disabled, the backend uses synthetic fixtures. Serper search is only enabled when both `SERPER_API_KEY` and `AAMAD_ENABLE_WEB_RESEARCH=true` are set.

The API exposes `POST /api/runs` to start a run, `GET /api/runs/{run_id}` to poll it, and `GET /healthz` for process health. Run state is held in memory, only one run may execute at a time, and results are not retained across backend restarts. Reports are advisory; recruiters remain responsible for reviewing recommendations and making all decisions.

---

## Getting Started

### Prerequisites

Before running the project, ensure you have:

- Python 3.11+
- Node.js and npm
- A valid OpenAI API key for CrewAI runs
- Optional: a Serper API key for search-enabled runs

### Environment Setup

Create and activate a virtual environment from the repository root, then install the backend and test dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

Set the required runtime and provider settings in the same PowerShell session that will run the backend:

```powershell
$env:AAMAD_TARGET_RUNTIME = "crewai"
$env:OPENAI_API_KEY = "your-openai-api-key"
$env:OPENAI_MODEL = "gpt-4o"
```

`AAMAD_TARGET_RUNTIME=crewai` selects the implemented backend runtime. `OPENAI_API_KEY` is required for actual CrewAI execution, including fixture-backed runs. For optional public web research, also set both of these values:

```powershell
$env:SERPER_API_KEY = "your-serper-api-key"
$env:AAMAD_ENABLE_WEB_RESEARCH = "true"
```

### Run the Application

In the activated backend terminal, start the API from the repository root:

```powershell
python -m uvicorn recruitment_assistant.api:app --app-dir src --host 127.0.0.1 --port 8000
```

In a second terminal, install and start the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The frontend proxies API requests to `http://127.0.0.1:8000`. The backend tests can be run from the repository root with `python -m pytest -q`; they stub the crew and do not require provider credentials.

To use the application, submit job requirements in the browser, optionally enter synthetic candidate profiles, then review the ranked advisory report when the run completes.

---

## Project Structure

This repository follows the AAMAD structure and keeps product and implementation artifacts organized by phase.

```text
recruitment-assistant/
├── AGENTS.md
├── CHECKLIST.md
├── README.md
├── aamad.config.yml
├── aamad.config.example.yml
├── pyproject.toml
├── src/recruitment_assistant/
│   ├── api.py
│   ├── crew.py
│   ├── fixtures.py
│   └── config/
├── frontend/
│   └── src/
├── project-context/
│   ├── 1.define/
│   ├── 2.build/
│   └── 3.deliver/
├── tests/
└── .env.example
```

### Key artifacts and locations

- `project-context/`: AAMAD product, architecture, build, and delivery artifacts
- `src/recruitment_assistant/`: FastAPI service, CrewAI orchestration, fixtures, and YAML configuration
- `frontend/`: React/Vite recruiter interface
- `tests/`: backend API and crew tests

---

## Development Status

### Current phase

The Build phase is complete. The backend, recruiter UI, and API integration are implemented, with fixture-based API verification.

### Completed

- Product requirements and solution architecture documented
- FastAPI run/status/health endpoints and CrewAI workflow implemented
- React/Vite recruiter interface integrated with asynchronous API polling
- Synthetic fixtures, safety-oriented report checks, and backend tests in place

### Next

- Complete Deliver-phase packaging and operational documentation
- Keep the MVP local or within an approved controlled demo; production hiring use is out of scope

---

## Development Notes

The current product scope intentionally keeps the MVP focused and safe:

- no full ATS integration
- no candidate communication automation
- no advanced analytics reporting in the mini-project
- no automated hiring decisions
- human review remains required throughout the workflow

This keeps the project practical for a first implementation while leaving a clear path for future growth.
