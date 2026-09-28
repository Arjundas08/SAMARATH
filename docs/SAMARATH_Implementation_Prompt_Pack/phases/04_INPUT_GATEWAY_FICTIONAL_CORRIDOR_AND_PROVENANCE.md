# Phase 04 - Input gateway, fictional corridor and provenance

Copy-ready implementation prompt. Run after: 01-03.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 10-14, 31-32.

Implement actual input entry and import using a shared adapter contract.

Provide TEST fixtures and authorized-export CSV/JSON adapters feeding the same normalizer, validation, persistence and snapshot service. A future integrated adapter may declare unavailable capabilities but must fail clearly as NOT_CONFIGURED; it must not return fabricated payloads or success. Do not implement unauthorized Railway scraping or claim public operational endpoints. XLSX may remain explicitly unsupported in this release rather than executing macros or guessing formulas.

Create a reproducible labelled fictional corridor with six fictional stations, distinct UP/DOWN resources, integer chainage, a junction/route conflict example, an electrical footprint affecting more than one track, and boundary reservations. Model source-to-resource mappings and explicit unresolved mappings. Include 60 monthly tasks, an up-to-30-task week, three departments, qualified resources, material/readiness facts, approved TEST_RULE recipes, timetable occupation and forecast vintages. Seed inputs only. Generated outcomes, selected packages and KPI numbers are forbidden.

Create small hand-checkable fixtures separately: normal, no-benefit, unknown compatibility, impossible mandatory deadline, cross-midnight, resource unavailable, partial execution and locked-conflict. Each includes assumptions, units, source badges and a fixture hash. Avoid designing every case to favor the optimizer.

Implement task/calendar/window/train-path edits as revisions with reason, actor and provenance. Import dry-run shows row errors; commit is atomic for the declared batch policy and idempotent by manifest/source version. Invalid records go to a quarantine view. File size/type/expansion limits and export formula safety are required. Protect imported source truth; corrections preserve lineage.

Freeze complete snapshots with exact membership and source freshness/quality. UNKNOWN mappings and missing required traffic/authority coverage block affected planning eligibility. TEST cannot be promoted by changing a badge. Implement Maintenance and Data screens backed by these APIs; all displayed counts come from database queries.

Acceptance: CSV/JSON and TEST adapters produce equivalent normalized behavior for equivalent input; duplicate import does not duplicate tasks; changed source version creates a revision; quarantine reasons are precise; scope checks hold; a user can edit a real record, reload and see it persisted. Show fixture provenance and snapshot hashes in evidence.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-04.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
