# Phase 09 - Monthly allocation and weekly reconciliation

Copy-ready implementation prompt. Run after: 08.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 20-21, 23, 38.

Implement the actual two-horizon contract, not independent month/week calendars.

The monthly model allocates tasks or validated packages to calendar-week intersections using authorized priority, release/due weeks, dependencies, existing commitments, conservative resource/occupation budgets and readiness conditions. Preserve units and map local calendar boundaries explicitly to UTC timestamps. Monthly output is ALLOCATED_PROVISIONAL. Aggregate budget feasibility is never described as an exact executable weekly schedule.

Provide a separate monthly validation scope. Record which weeks have undergone detailed checking. A conditional future task has a named prerequisite, owner and ready-by condition; it cannot quietly become READY when refined. Respect cross-month carry-in/out and tasks that cross a week boundary according to an explicit documented policy. A boundary rule must not be invented from convenience.

Weekly SolveRequest pins the parent monthly version and current weekly snapshot. The weekly solver respects parent allocations and preserved reservations. Moving a task to another week, adding emergency demand or changing reserved capacity creates a ReconciliationCase or explicit amendment. An otherwise model-valid child awaiting parent reconciliation is not programme-approval eligible.

Create a controlled reconciliation path: identify implicated allocations; present changes; allow an authorized user to revise the parent; regenerate the child from the new immutable versions. Do not infer a general valid capacity cut from a single failed heuristic. Old versions remain inspectable.

Calculate monthly allocation/mandatory coverage, conditional work, resource pressure, deferred work and detailed-validation coverage from actual results. Expose the difference between unallocated, infeasible-in-declared-domain and search incomplete. No empty week should be labelled optimally planned by default.

Acceptance: a month with ample aggregate hours but impossible detailed windows raises a reconciliation case; weekly change within permitted parent bounds needs no fabricated amendment; cross-week move requires one; emergency intake is visible; completed work is not rescheduled; mandatory deadlines remain hard. Save parent/child/version lineage and tests for month/week boundary behavior. Make API contracts ready for the planning UI without drawing fictitious results.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-09.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
