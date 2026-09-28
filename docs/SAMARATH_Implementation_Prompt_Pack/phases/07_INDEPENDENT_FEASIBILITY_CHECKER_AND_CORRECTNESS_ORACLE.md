# Phase 07 - Independent feasibility checker and correctness oracle

Copy-ready implementation prompt. Run after: 05-06.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 23, 41.

Implement the separate deterministic checker before allowing optimizer output to become a proposal.

The checker reads raw snapshot records, rule/topology versions and materialized assignments, not eligibility flags from the planner. It may import contracts and low-level non-semantic utilities, but not planner/optimizer candidate, overlap, capacity, compatibility or dependency predicates. Add an import-boundary test. Design its interval sweep and capacity evaluation independently and document shared-assumption risks; this is not safety certification.

Verify task duplication and mandatory coverage; release/deadline constraints; original-resolution train and fixed-authority occupation; full window containment; crew/machine/skill/calendar capacity; travel/setup; complete package compatibility and restoration; readiness; dependencies; location validity; preserved locks; boundary carry-in/out; and the prohibition on autonomous authority transitions. Unknown mandatory facts invalidate a weekly publishable proposal. Return VALID or INVALID with exact code, entity IDs, observed/expected values, units and source references. A VALID verdict refers only to the specified model/evidence set.

Create hand-authored tiny valid and invalid assignment files that do not depend on the candidate generator. Add an exhaustive tiny-instance oracle for later solver correctness checks. Make it independent enough to catch missing candidate constraints, and document its limited scope/size. Do not equate matching two implementations that share the same predicate with independent verification.

Mutation tests must reject: a one-second overlap; a missing restoration phase; duplicate task; wrong qualified resource; a three-way capacity violation; a moved hard lock; an unresolved footprint; broken dependency; incorrect cross-midnight boundary; missing mandatory task; and an unobserved release used to free a resource. Include valid adjacency cases only when the required clearance/protection conditions are represented.

Run the baseline from Phase 06 through the checker. Persist checker version and results independently; no client can edit the verdict. If the baseline fails, fix the producer or the documented model, not the checker to accommodate a known violation.

Acceptance: all expected golden and mutation outcomes pass; shared predicate imports fail CI; original-resolution errors are found despite minute-level candidate starts; persisted results reproduce from the same input files. Obtain separate human/domain review when available and record when it is still missing.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-07.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
