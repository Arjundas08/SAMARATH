# Phase 17 - Failure recovery, security and scaling evidence

Copy-ready implementation prompt. Run after: 00-16.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 33-34, 41-43, 51, 55-58.

Harden and benchmark the actual bounded application. This phase must produce evidence, not a 'production-ready' badge.

Run the requirement-linked regression suite, tiny exhaustive oracle, checker mutations, PostgreSQL/API integration and browser journeys. Add failure injection for worker termination, lease expiration, database/identity outage, stale run publication, retry storms, malformed imports, partial batch failure and approval concurrency. Invalid or unavailable data must never yield a silently current approved proposal.

Review OIDC/session/CSRF/CORS controls, role/territory isolation, RLS pool reuse, secrets, dependency/image vulnerabilities, import limits, export formula safety and log redaction. Use maintained security checks and record actual findings and fixes. Do not claim certification or zero vulnerabilities solely from a scanner. Security fixes need regression tests that demonstrate the previously possible failure.

Benchmark declared synthetic workloads at 10, 30 and 100 tasks with multiple seeds and varied window density, package choices and resource contention. Attempt 300 tasks only as an explicitly exploratory case after smaller workloads remain safe and within resource limits. Measure candidate generation, conflicts/model construction, CP-SAT stages, checker, API round trip, peak memory, status and domain truncation separately. Use repeated runs and report sample count, median and tail behavior. Name hardware/configuration; do not extrapolate to a whole division from task counts.

The blueprint's 30-task/30-second weekly and 60-task/60-second monthly budgets are engineering targets, not established facts. Keep resource caps and honest timeout behavior even if targets fail. Profile first; optimize the dominant cost with sparse indexing or a documented CP-SAT representation change. Re-run correctness oracle and checker tests after any model optimization. No test-set-specific canned shortcut.

Exercise backup and restore in a disposable environment; measure what was restored and how long it took. Verify a release can run offline with pre-pulled images, local auth, fonts and TEST data. Runtime must not secretly depend on analytics/CDN/external AI. Record any gap against proposed RPO/RTO instead of marking it passed without a drill.

Acceptance: reproducible benchmark report with raw results; classified unresolved issues; no known critical authorization or false-feasibility defect accepted for demonstration; failure paths visible and recoverable; an honest measured supported envelope. If a core gate fails, fix it or mark release blocked—never compensate with presentation polish.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-17.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
