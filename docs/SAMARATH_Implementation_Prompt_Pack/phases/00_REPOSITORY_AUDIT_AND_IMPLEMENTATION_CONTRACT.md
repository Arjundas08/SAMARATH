# Phase 00 - Repository audit and implementation contract

Copy-ready implementation prompt. Run after: None.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 1-9, 29-33, 44-48.

Implement Phase 00 only. Establish an executable development plan grounded in this repository; do not generate the whole application yet.

Inspect the working tree, existing services, migrations, tests, dependency files and local instructions. Identify useful code to preserve. If no application exists, define the monorepo layout from the blueprint with one Python package graph; actual scaffolding is Phase 01. Read the blueprint, addendum and frontend design brief. Summarize any contradictions with the current code and resolve routine implementation choices through documented ADRs.

Create docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md, docs/DECISIONS.md, docs/SCOPE.md and docs/API_CONTRACT.md. Map the 20 core phases to requirement IDs, owner skill, prerequisites, evidence and exit gates. Mark every capability as existing-and-tested, existing-unverified, missing or deferred. Do not mark an unimplemented capability as done because its design is written.

Freeze the bounded TEST corridor scope, units, UTC storage/Asia-Kolkata display, immutable revision strategy, three data modes and separate demand/programme/authority states. Define the exact two objective profiles from the addendum, including coverage protection before stability in recovery mode. Freeze API names around the blueprint; add explicit CRUD/revision contracts for resource calendars, train occupations, windows and topology needed for arbitrary evaluator edits. Do not invent external Railway endpoints.

Specify source-of-truth contracts for Task, Snapshot, CandidateManifest, MaterializedAssignment, SolverRun, ValidationResult, PlanVersion, Reason, PlanDiff and PlanMetric. Include run/snapshot/version relationships, status enums and structured errors. Define which fields are server-derived. Record the expected database ownership and validator import boundary.

Review current official dependency documentation only where needed to select mutually compatible supported versions; record sources and pinning plan. Define canonical commands for install, migrate, seed, run API/web/worker, unit/integration/browser tests and production build. Flag environment gaps honestly. Do not train ML or claim SIH rule confirmation from the older guideline.

Acceptance: every phase has an unambiguous gate; no competing versions of the same API contract; all unresolved Railway facts are explicit; the implementation state matches inspected code. Return the first runnable phase and any real blocker. This phase produces project-control documents, not a claim of a working prototype.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-00.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
