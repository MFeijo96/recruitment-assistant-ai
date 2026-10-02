export type RunStatus = "queued" | "running" | "succeeded" | "failed";

type RunResponse = {
    run_id: string;
    status: RunStatus;
    report_markdown?: string;
    error?: { code: string; message: string };
};

type ErrorResponse = {
    error?: { message?: string };
};

async function request<T>(path: string, init: RequestInit): Promise<T> {
    let response: Response;
    try {
        response = await fetch(path, init);
    } catch {
        throw new Error("Could not reach the backend. Check that the API is running on 127.0.0.1:8000.");
    }

    const payload = await response.json().catch(() => null) as T & ErrorResponse | null;
    if (!response.ok) {
        throw new Error(payload?.error?.message ?? `The backend returned HTTP ${response.status}.`);
    }
    if (payload === null) {
        throw new Error("The backend returned an invalid response.");
    }
    return payload;
}

function waitForNextPoll(signal: AbortSignal): Promise<void> {
    return new Promise((resolve, reject) => {
        const timer = window.setTimeout(() => {
            signal.removeEventListener("abort", abort);
            resolve();
        }, 1000);
        const abort = () => {
            window.clearTimeout(timer);
            reject(new DOMException("The run was cancelled.", "AbortError"));
        };
        signal.addEventListener("abort", abort, { once: true });
        if (signal.aborted) abort();
    });
}

export async function runShortlist(
    jobRequirements: string,
    candidateProfiles: string,
    signal: AbortSignal,
    onStatus: (status: RunStatus) => void,
): Promise<string> {
    const accepted = await request<RunResponse>("/api/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            job_requirements: jobRequirements,
            candidate_profiles: candidateProfiles,
        }),
        signal,
    });
    onStatus(accepted.status);

    const deadline = Date.now() + 490_000;
    while (Date.now() < deadline) {
        await waitForNextPoll(signal);
        const run = await request<RunResponse>(`/api/runs/${encodeURIComponent(accepted.run_id)}`, { signal });
        onStatus(run.status);

        if (run.status === "succeeded") {
            if (!run.report_markdown) throw new Error("The run completed without a report.");
            return run.report_markdown;
        }
        if (run.status === "failed") {
            throw new Error(run.error?.message ?? "The shortlist run failed.");
        }
        if (run.status !== "queued" && run.status !== "running") {
            throw new Error("The backend returned an unknown run status.");
        }
    }

    throw new Error("The backend did not finish within the expected run window.");
}