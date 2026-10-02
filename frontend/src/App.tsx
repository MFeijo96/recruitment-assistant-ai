import { useRef, useState, type FormEvent } from "react";
import { runShortlist, type RunStatus } from "./api";
import {
    ArrowUpRight,
    BriefcaseBusiness,
    Check,
    CircleHelp,
    Clock3,
    FileText,
    Plus,
    ShieldCheck,
    TriangleAlert,
} from "lucide-react";

const MAX_BRIEF_LENGTH = 12000;

export default function App() {
    const [requirements, setRequirements] = useState("");
    const [profiles, setProfiles] = useState("");
    const [error, setError] = useState("");
    const [status, setStatus] = useState<RunStatus | "idle">("idle");
    const [report, setReport] = useState("");
    const activeRequest = useRef<AbortController | null>(null);
    const isRunning = status === "queued" || status === "running";

    async function submitBrief(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        if (!requirements.trim()) {
            setError("Add the role requirements before starting a shortlist.");
            return;
        }

        setError("");
        setReport("");
        const controller = new AbortController();
        activeRequest.current = controller;
        setStatus("queued");
        try {
            const completedReport = await runShortlist(
                requirements.trim(),
                profiles,
                controller.signal,
                setStatus,
            );
            setReport(completedReport);
        } catch (caught) {
            if (!controller.signal.aborted) {
                setError(caught instanceof Error ? caught.message : "The shortlist run failed.");
                setStatus("failed");
            }
        } finally {
            if (activeRequest.current === controller) activeRequest.current = null;
        }
    }

    function resetSession() {
        activeRequest.current?.abort();
        activeRequest.current = null;
        setRequirements("");
        setProfiles("");
        setError("");
        setReport("");
        setStatus("idle");
    }

    return (
        <div className="app-shell">
            <aside className="sidebar" aria-label="Workspace">
                <a className="brand" href="#main" aria-label="Recruitment Assistant home">
                    <span className="brand-mark"><BriefcaseBusiness size={19} strokeWidth={2.2} /></span>
                    <span className="brand-name">Recruitment<span>Assistant</span></span>
                </a>

                <div className="workspace-label">WORKSPACE</div>
                <button className="new-session" type="button" onClick={resetSession}>
                    <Plus size={17} />
                    <span>New shortlist</span>
                    <span className="key-hint">N</span>
                </button>

                <div className="sidebar-section">
                    <div className="section-label">RECENT</div>
                    <p className="empty-history">Your session history is empty.</p>
                </div>

                <div className="sidebar-bottom">
                    <div className="local-state"><span className="state-dot" /> Local session</div>
                    <p>Briefs and reports stay in memory for this session.</p>
                </div>
            </aside>

            <main id="main" className="main-area">
                <header className="topbar">
                    <div className="breadcrumb"><span>Workspace</span><span className="breadcrumb-slash">/</span><strong>New shortlist</strong></div>
                    <div className="topbar-actions">
                        <span className="env-label"><span className="env-dot" /> DEMO ENVIRONMENT</span>
                        <button className="icon-button" type="button" aria-label="About this workspace" title="About this workspace">
                            <CircleHelp size={18} />
                        </button>
                    </div>
                </header>

                <div className="content-grid">
                    <section className="workflow-column" aria-labelledby="page-title">
                        <div className="page-intro">
                            <div className="eyebrow"><span className="eyebrow-rule" /> CANDIDATE REVIEW</div>
                            <h1 id="page-title">Build a shortlist</h1>
                            <p>Start with the role. Add synthetic profiles if you have them.</p>
                        </div>

                        <form className="brief-form" onSubmit={submitBrief} noValidate>
                            <div className="field-heading">
                                <label htmlFor="requirements">Role requirements <span className="required-mark">*</span></label>
                                <span className="field-meta">JOB BRIEF</span>
                            </div>
                            <textarea
                                id="requirements"
                                value={requirements}
                                maxLength={MAX_BRIEF_LENGTH}
                                onChange={(event) => {
                                    setRequirements(event.target.value);
                                    if (error) setError("");
                                }}
                                placeholder="Describe the role, essential skills, experience, and any must-have criteria..."
                                aria-describedby="requirements-hint requirements-count"
                                aria-invalid={Boolean(error)}
                                rows={8}
                            />
                            <div className="field-footnote">
                                <span id="requirements-hint">Use job-related criteria. Avoid protected or sensitive traits.</span>
                                <span id="requirements-count">{requirements.length.toLocaleString()} / {MAX_BRIEF_LENGTH.toLocaleString()}</span>
                            </div>

                            <details className="profiles-details">
                                <summary>
                                    <span className="summary-leading"><Plus size={16} /> Add candidate profiles</span>
                                    <span className="optional-label">OPTIONAL</span>
                                </summary>
                                <label className="sr-only" htmlFor="profiles">Synthetic candidate profiles</label>
                                <textarea
                                    id="profiles"
                                    className="profiles-input"
                                    value={profiles}
                                    onChange={(event) => setProfiles(event.target.value)}
                                    placeholder="Paste synthetic or fixture profiles here. Separate profiles with a blank line."
                                    rows={5}
                                />
                                <p className="profiles-note"><ShieldCheck size={14} /> Use synthetic or fixture data only in this demo.</p>
                            </details>

                            {error && <div className="form-message error-message" role="alert"><TriangleAlert size={17} />{error}</div>}
                            <div className="submit-row">
                                <span className="submit-note"><Clock3 size={15} /> Runs can take up to 8 minutes</span>
                                <button className="submit-button" type="submit" disabled={isRunning}>
                                    <span>{isRunning ? "Running shortlist" : "Run shortlist"}</span><ArrowUpRight size={17} />
                                </button>
                            </div>
                        </form>

                        <section className="report-section" aria-labelledby="report-title">
                            <div className="report-heading">
                                <div>
                                    <div className="eyebrow"><span className="eyebrow-rule" /> OUTPUT</div>
                                    <h2 id="report-title">Shortlist report</h2>
                                </div>
                                <span className={`report-state report-state-${status}`} aria-live="polite">
                                    <span className={`state-dot ${status === "idle" ? "muted" : ""}`} />
                                    {status === "idle" ? "AWAITING RUN" : status.toUpperCase()}
                                </span>
                            </div>
                            {report ? (
                                <pre className="report-content" aria-label="Shortlist report">{report}</pre>
                            ) : (
                                <div className="report-empty" aria-busy={isRunning}>
                                    <span className="report-icon"><FileText size={20} /></span>
                                    <div>
                                        <strong>{isRunning ? "Building your shortlist" : status === "failed" ? "Run did not complete" : "Your report will appear here"}</strong>
                                        <p>{isRunning ? "The crew is researching, evaluating, and ranking candidates." : "Ranked recommendations, evidence, and outreach drafts are shown after a completed run."}</p>
                                    </div>
                                </div>
                            )}
                            <div className="advisory-line"><ShieldCheck size={16} /><span>Decision support only. Recruiter review is required.</span></div>
                        </section>
                    </section>

                    <aside className="run-aside" aria-label="Run information">
                        <div className="aside-heading"><span>RUN SETTINGS</span><span className="settings-check"><Check size={13} /> READY</span></div>
                        <div className="setting-row">
                            <span className="setting-icon fixture-icon"><FileText size={16} /></span>
                            <span className="setting-copy"><strong>Candidate source</strong><small>Profiles or bundled fixtures</small></span>
                        </div>
                        <div className="setting-row">
                            <span className="setting-icon time-icon"><Clock3 size={16} /></span>
                            <span className="setting-copy"><strong>Run limit</strong><small>Up to 8 minutes</small></span>
                        </div>
                        <div className="aside-divider" />
                        <div className="safety-note">
                            <ShieldCheck size={18} />
                            <div><strong>Human-led decisions</strong><p>No automatic hire/reject decisions or messages are sent.</p></div>
                        </div>
                        <div className="aside-footer">Use fixture or synthetic candidate data only.</div>
                    </aside>
                </div>
            </main>
        </div>
    );
}