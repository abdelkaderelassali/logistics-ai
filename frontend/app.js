const API_BASE = "/api";

const state = { loading: false };

const formEl = document.getElementById("request-form");
const requestInputEl = document.getElementById("request-input");
const submitBtnEl = document.getElementById("submit-btn");
const charCountEl = document.getElementById("char-count");
const workflowEl = document.getElementById("workflow-timeline");
const resultsContainerEl = document.getElementById("results-container");
const metaOutputEl = document.getElementById("meta-output");
const statusBadgeEl = document.getElementById("status-badge");

const STEP_NAMES = [
    "Parsing Request",
    "Searching Regulations",
    "Checking Fleet",
    "Route Optimization",
];

document.addEventListener("DOMContentLoaded", () => {
    formEl.addEventListener("submit", onSubmit);
    requestInputEl.addEventListener("input", () => {
        charCountEl.textContent = requestInputEl.value.length;
    });

    renderWorkflowSkeleton();
    syncHealth();
});

async function syncHealth() {
    try {
        const health = await fetchJSON(`${API_BASE}/health`);
        statusBadgeEl.textContent = health.api_key_configured ? "Ready" : "API Key Missing";
    } catch {
        statusBadgeEl.textContent = "Offline";
    }
}

async function onSubmit(e) {
    e.preventDefault();
    if (state.loading) return;

    const request = requestInputEl.value.trim();
    if (request.length < 10) {
        metaOutputEl.textContent = "Please write a longer logistics request.";
        return;
    }

    state.loading = true;
    submitBtnEl.disabled = true;
    submitBtnEl.textContent = "Running workflow...";
    metaOutputEl.textContent = "The workflow is running step by step.";

    setWorkflowState("running");

    try {
        const result = await fetchJSON(`${API_BASE}/process`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ request }),
        });

        renderWorkflow(result.workflow || []);
        renderResults(result);
        metaOutputEl.textContent = "User Request → AI Agents → RAG Retrieval → Validation → Final Response";
        statusBadgeEl.textContent = "Completed";
    } catch (err) {
        metaOutputEl.textContent = `Error: ${err.message}`;
        statusBadgeEl.textContent = "Error";
    } finally {
        state.loading = false;
        submitBtnEl.disabled = false;
        submitBtnEl.textContent = "Run AI Workflow";
    }
}

function renderWorkflowSkeleton() {
    workflowEl.innerHTML = STEP_NAMES.map((name, index) => `
        <div class="timeline-item pending" data-step="${index}">
            <div class="timeline-main">
                <span class="spinner"></span>
                <div>
                    <strong>${index + 1}. ${escapeHtml(name)}</strong>
                    <div class="step-subtitle">Waiting</div>
                </div>
            </div>
            <span class="pill">Pending</span>
        </div>
    `).join("");
}

function setWorkflowState(mode) {
    const items = workflowEl.querySelectorAll(".timeline-item");
    items.forEach((item) => {
        item.className = "timeline-item pending";
        item.querySelector(".pill").textContent = "Pending";
    });
    if (mode === "running") {
        items.forEach((item, idx) => {
            item.classList.remove("pending");
            item.classList.add("running");
            item.querySelector(".pill").textContent = idx === 0 ? "Running" : "Pending";
            if (idx === 0) item.querySelector(".step-subtitle").textContent = "Processing";
        });
    }
}

function renderWorkflow(workflow) {
    const items = workflowEl.querySelectorAll(".timeline-item");
    items.forEach((item, idx) => {
        const step = workflow[idx];
        item.className = "timeline-item done";
        item.querySelector(".pill").textContent = "Done";
        item.querySelector(".pill").classList.add("done");
        item.querySelector(".step-subtitle").textContent = step?.timestamp ? step.timestamp.split("T")[1].slice(0, 8) : "Completed";
        const spinner = item.querySelector(".spinner");
        if (spinner) spinner.replaceWith(makeCheckMark());
    });
}

function renderResults(result) {
    const cards = [
        ["Search", result.rag_context],
        ["Analysis", result.analysis_plan],
        ["Validation", result.validation_report],
        ["Final Response", result.final_response],
    ];

    resultsContainerEl.innerHTML = cards
        .map(([title, text], index) => `
            <article class="result-card ${index === 3 ? "final" : ""}">
                <h3>${escapeHtml(title)}</h3>
                <pre>${escapeHtml(text || "No output")}</pre>
            </article>
        `)
        .join("");
}

function makeCheckMark() {
    const span = document.createElement("span");
    span.textContent = "DONE";
    span.style.color = "var(--ok)";
    span.style.fontWeight = "800";
    return span;
}

async function fetchJSON(url, options = {}) {
    const response = await fetch(url, options);
    if (!response.ok) {
        let detail = `Request failed (${response.status})`;
        try {
            const body = await response.json();
            detail = body.detail || detail;
        } catch {
            // ignore
        }
        throw new Error(detail);
    }
    return response.json();
}

function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value || "";
    return div.innerHTML;
}
