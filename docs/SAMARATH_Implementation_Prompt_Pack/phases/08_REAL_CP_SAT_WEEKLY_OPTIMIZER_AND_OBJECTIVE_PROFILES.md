# Phase 08 - Real CP-SAT weekly optimizer and objective profiles

Copy-ready implementation prompt. Run after: 06-07.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 17-19, 22-23, 27, 42 plus addendum.

Implement a real bounded weekly optimizer in OR-Tools CP-SAT. Do not add a second production solver.

Start with the finite-placement formulation: one Boolean per candidate, at-most-once task coverage, equality for mandatory tasks, explicit incompatibility/capacity/dependency constraints, preserved locks, and resource-time occupation derived without double-counting. Candidate eligibility must not be the only defense: independently check the result against the raw snapshot. Build sparse model structures; do not allocate a full candidate-by-resource-by-minute tensor when sparse intervals suffice.

Implement versioned lexicographic PROGRAMME_IMPROVEMENT and DISRUPTION_RECOVERY profiles from the implementation addendum. Define every integer objective and its units. Hard feasibility and mandatory work are never relaxed. Recovery preserves the declared required/critical coverage policy and protected commitments, then minimizes changed assignments and movement before marginal efficiency. Avoid allowing a one-minute efficiency gain to rearrange many tasks in recovery mode. Document exactly where optional coverage and permitted tardiness sit in each profile.

Solve stages under a single total wall-time budget, tracking remaining time, stage status, incumbent and bound. Freeze a stage value only when OPTIMAL. On FEASIBLE/time limit, stop lower stages and return the qualified incumbent for checking. On UNKNOWN with no incumbent, do not create a successful plan. Handle MODEL_INVALID as an engineering fault. Surface domain truncation separately from solver status. A bound is associated with its specific objective stage; do not invent an overall gap across heterogeneous objectives.

Persist parameters, seed, worker count, software/model version, snapshot and candidate-manifest hashes, timings and assignment phases. Validate before publishing. Preserve an earlier valid incumbent across later stage interruption only if its exact lineage and stage claims remain correct. Cancellation must not produce a false completed result.

Acceptance: tiny exhaustive-oracle agreement on feasible objective values; mandatory impossibility; unknown-rule exclusion; no duplicate coverage; preserved locks; timeout with and without incumbent; deterministic single-worker regression semantics; recovery chooses the less disruptive option in a constructed counterexample. Compare against the credible greedy baseline on equal inputs and equal coverage. Record generation/model/solve/check time and memory for 10/30 tasks. A representation change requires an ADR and repeated oracle/checker tests.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-08.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
