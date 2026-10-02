# Frontend Build: Recruitment Assistant

**Status:** UI and API flow integrated; frontend build and browser verification pending
**Persona/action:** `@frontend-eng` / `*develop-fe`  
**Inputs reviewed:** `project-context/1.define/prd.md`, `project-context/1.define/sad.md`

## Decisions

- Implemented the SAD's React, Vite, and TypeScript web client in `frontend/`.
- The integration step connects `POST /api/runs` and polls `GET /api/runs/{run_id}` through the Vite development proxy; see `project-context/2.build/integration.md`.
- The screen provides a required role brief, optional free-text candidate profiles, a run action, visible validation/connection feedback, a report destination, and human-review/synthetic-data notices.
- A successful API response displays its report as escaped text. No report is fabricated and raw HTML is not enabled.
- Inputs and notices are held only in component memory; no browser persistence or session history is implemented.
- Responsive desktop-first layout, keyboard-operable native form controls, text-based errors, reduced-motion support, and responsive mobile layout are included.
- `project-context/2.build/setup.md` was not present in the workspace, so no setup artifact was available to review.

## Status

- [x] Build the recruiter shortlist interface and responsive styling.
- [x] Add required-field validation and an honest pre-integration submission state.
- [x] Document safety and data-retention constraints in the UI.
- [ ] Install dependencies and run the Vite production build.
- [x] Connect the API, queued/running/succeeded/failed states, and safe report rendering.
- [ ] Verify the integrated fixture workflow and browser accessibility.

## Run Locally

Requires Node.js and npm. From `frontend/`, run `npm install`, then `npm run dev`; Vite is configured for `http://127.0.0.1:5173` to match the backend's default development CORS origin. Run `npm run build` for a production build.

## Verification Notes

The current environment does not have `node` or `npm`, so dependencies could not be installed and the frontend build/browser smoke test could not be run. The offline API round-trip is verified by the backend API tests; this does not verify rendering in a browser.

## Sources

- `project-context/1.define/prd.md` — user roles, P0 workflow, safety policy, and acceptance criteria.
- `project-context/1.define/sad.md` — frontend stack, run/status contract, and UI requirements.
- `.cursor/agents/frontend-eng.md` — `*develop-fe` scope and UI-only boundary.

## Assumptions

- The initial environment remains a local internal demo and uses fixture or synthetic candidate data only.
- The frontend is served at `http://127.0.0.1:5173`; the backend owns run execution and status polling.
- Integration will connect the form to the existing API contract without persisting candidate data in the browser.

## Open Questions

No product or UI decisions remain open. API wiring, dependency installation, and integrated acceptance are implementation handoffs, not unresolved product decisions.

## Audit

- **Timestamp:** 2026-10-02
- **Persona/action:** `frontend-eng` / `develop-fe`, `document-frontend`
- **Decision:** Keep candidate data session-only and render report content as escaped text.
- **Verification:** Offline API round-trip tests pass; Vite build and browser smoke test are unavailable because Node.js/npm are not installed.