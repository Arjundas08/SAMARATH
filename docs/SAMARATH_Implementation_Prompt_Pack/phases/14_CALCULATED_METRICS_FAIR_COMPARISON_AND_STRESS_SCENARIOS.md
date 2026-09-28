# Phase 14 - Calculated metrics, fair comparison and stress scenarios

Copy-ready implementation prompt. Run after: 08-13.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 26, 37-40.

Implement a versioned metric calculator and a defensible evaluation view. No release KPI may be stored as an editable demo constant.

Calculate mandatory/critical on-time coverage, unscheduled reasons, permitted lateness, union infrastructure occupation, comparable-task changes, total time movement, lock preservation, explanation coverage, run/model/generation/check timings and domain size. Modelled availability uses declared resource weights and horizon denominators, with fixed closures shown separately. Count the union per resource, not the sum of task durations. Show units and N/A on zero denominators.

Every result pins snapshot, plan/run, calculator, rule/policy and domain versions. Comparison requires the same workload, horizon, resource scope and declared planning domain. Display coverage before occupation gain. If the greedy baseline finds no valid plan, show that outcome; do not fabricate a percentage improvement against an invalid or zero baseline. A lower-coverage proposal must not appear superior merely because it occupies less track.

Implement fixed-plan stress testing with versioned declared TEST perturbations: work duration increases, late resource, shifted goods forecast and urgent work. Recompute phase consequences and independently validate the unchanged policy/assignment decision. Separate actual rule changes that invalidate a package from simple duration effects. Show passed scenarios, failures, first/all reasons, worst excess and mandatory impact. Scenario pass share is not a calibrated reliability probability.

Adaptive re-solving under a perturbed snapshot is a separate experiment with runtime, new version and PlanDiff. Run baseline and optimizer under identical stress scenarios. Do not blend fixed-plan resilience and recovery success into one misleading score.

Build a quiet comparison view with aligned denominators, explanatory tooltips, source badges and exportable raw data. Include no-benefit and optimizer-underperformance cases. Persist enough to reproduce a result on the same input artifacts; parallel solve ties need not reproduce bit-identical assignments.

Acceptance: hand-calculated union test with overlapping tasks and multi-track electrical footprint; zero-denominator test; unequal-coverage comparison warning; changed-task denominator test; stale metrics never attributed to new inputs; scenario '8 of 10' displayed as a count only; actual baseline/optimizer reports from the pipeline. Mark every performance number as measured on named hardware or as an untested target.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-14.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
