# Phase 01 - Runnable foundation, database and typed contracts

Copy-ready implementation prompt. Run after: 00.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 11-13, 29, 31, 43, 47.

Implement a clean runnable foundation in the existing repository, preserving unrelated work.

Create apps/web, apps/api, the modular Python packages, workers, adapters, db/migrations, scenarios, tests and infra only as needed. Wire React/TypeScript, FastAPI, PostgreSQL and Compose with pinned dependencies and lockfiles. Keep CPU planning work out of request handlers. Provide .env.example without real secrets, health/readiness checks, structured logs, developer instructions and reproducible commands. Health must distinguish a reachable process from a usable database.

Implement initial migrations for identities/scopes, sources/connectors, revision envelopes, topology resources/mappings, maintenance tasks/requirements, calendars, windows, train occupation, snapshots/membership, policy versions, jobs/outbox, run/result skeletons and audit events. Add detailed business tables in later phases through migrations. Document how every blueprint entity is implemented, grouped or deferred. Do not create dozens of empty repositories merely to mirror an entity list.

Every versioned record has stable identity and immutable revision identity, provenance and territory scope. Use database keys, uniqueness and check constraints for required invariants; prevent snapshot references to mutable content. Use integer seconds/metres and typed units. Define canonical serialization and stable hashing of snapshots with sorted membership, explicit timestamp representation and versioned schemas; never hash an unordered mutable JSON object opportunistically.

Create Pydantic contracts and generate a TypeScript API client/types from OpenAPI. Define enums independently for job state, solver status, stop reason, domain completeness, validation, applicability, provenance and approval eligibility. Reject unexpected enum values and invalid units. No fabricated successful solver endpoint.

Test migrations on an empty disposable PostgreSQL database and a representative upgrade; verify revision uniqueness, FK integrity, stable snapshot hash under equivalent ordering, changed hash on actual content revision, and schema/client generation. Use PostgreSQL for DB integration tests rather than substituting SQLite semantics. Include smoke checks for API/web startup and a production frontend build.

Acceptance: documented commands reproduce the scaffold; real PostgreSQL persistence works; migrations and typed contracts pass their targeted checks; service unavailability is visible. Solver and integration capabilities are explicitly unimplemented.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-01.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
