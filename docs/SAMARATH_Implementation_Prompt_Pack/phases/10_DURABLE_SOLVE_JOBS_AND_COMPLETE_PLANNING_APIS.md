# Phase 10 - Durable solve jobs and complete planning APIs

Copy-ready implementation prompt. Run after: 02, 08-09.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 28, 31, 33-34, 42-43.

Expose the real planning pipeline through durable asynchronous APIs and a separate worker.

Implement the agreed /api/v1 routes for snapshots, monthly/weekly solves, run status/cancellation, immutable plan versions, validation, candidate/unscheduled evidence and sources. A request validates scope, policy, snapshot and budget, commits a job/outbox/audit transaction and returns 202 with run ID and status URL. The request handler must not block on CPU solving. Fake successful handlers are unacceptable.

Use PostgreSQL FOR UPDATE SKIP LOCKED for short job-claim transactions. Solve outside transactions with a lease, heartbeat and fencing token. Publication checks current ownership/token and unique result keys; expired workers cannot publish twice or overwrite a newer result. Implement bounded retry and a visible failed-job state. At-least-once delivery requires idempotency; do not claim exactly-once execution.

Use Idempotency-Key for mutations and If-Match for mutable aggregate commands. Define request-fingerprint conflict behavior, stale ETags, validation errors, role denials, rate limits and dependency failure responses. A completed INFEASIBLE run is a domain outcome, not HTTP 500. Separate HTTP state, job state, solver result, checker verdict, applicability and approval eligibility in schemas.

Detect snapshot obsolescence while a run is in flight. Preserve historical artifacts but prevent silent activation of obsolete results. Return genuine status transitions; no simulated progress percentage or promised completion time. Implement modest scoped polling with cancellation/backoff in the frontend API layer; use generated types. Do not add WebSockets simply for appearances.

Acceptance integration tests with real PostgreSQL: duplicate submit; mismatched key/body; stale ETag; worker crash; lease expiry; stale worker publication; source update during solve; cancellation; unauthorized run access; API/database outage. Verify only a checked, correctly versioned result can be presented as usable. Show a browser-started real solve reaching a persisted outcome through this path.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-10.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
