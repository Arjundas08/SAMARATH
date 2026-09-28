# Phase 13 - Event-driven stable replanning and PlanDiff

Copy-ready implementation prompt. Run after: 09-12.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 27-28, 34 plus addendum.

Implement the dynamic capability that the evaluator can challenge with an arbitrary valid edit.

Accept versioned, idempotent events for task/criticality/deadline, train/forecast occupation, resources, windows, rule/topology, locks/rejections and execution observations. Validate source order and scope. In one transaction persist the revision/audit/outbox event and invalidate affected plan applicability. An old approved artifact remains historically approved while its current usability becomes STALE or BLOCKED.

Build impact closure across package membership, dependencies, shared resources, overlapping affected footprints and parent/boundary commitments. Preserve completed work, continuing external occupation and hard planner commitments. Missing actual release never frees a resource by elapsed planned time. Start with a limited repair neighborhood; expand under a bounded policy if necessary. Disclose restricted search scope; do not call it globally minimum-change.

Use DISRUPTION_RECOVERY objectives with the coverage protection already frozen. Minimize changed comparable assignments before marginal efficiency gains. Define changed as time/resource/recipe/week/removal changes, not only a moved start. Keep added work separate in denominators. A conflicting hard lock creates escalation, never automatic unlock. Parent changes require reconciliation.

Implement queue debounce/coalescing using the durable mechanism from Phase 10. Immediate applicability invalidation must not wait for debounce. A bounded number of pending jobs can coalesce while preserving every underlying event in the audit trail. Source order and fencing prevent obsolete results becoming current. Avoid solve storms from the worker's own result-write events.

Calculate PlanDiff: unchanged, shifted, resource changed, repackaged, added, cancelled, now unscheduled and completed. Store from/to versions and reason/event links. Distinguish actual cancellation from an omitted assignment and from residual work. Show a useful synchronized before/after chart and a textual diff, with uncertainty visible.

Acceptance browser tests: judge changes a machine, deadline, train occupation, window and rule; each revision follows the same solver/checker pipeline. Include irrelevant edit with legitimately unchanged assignments; event storm; out-of-order event; edit during solve; preserved hard lock; conflicting lock; partial execution; and a case where recovery preserves more assignments than programme-improvement mode. No predefined edit-to-result mapping may exist.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-13.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
