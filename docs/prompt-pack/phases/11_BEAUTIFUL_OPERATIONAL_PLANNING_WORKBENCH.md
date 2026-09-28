# Phase 11 - Beautiful operational planning workbench

Copy-ready implementation prompt. Run after: 03-05, 09-10.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 31-32, DESIGN_BRIEF.md.

Implement the signature SAMARATH workbench on real APIs and stored TEST records. Read DESIGN_BRIEF.md in full and preserve the established design tokens.

Build Monthly and Weekly views under Planning. Monthly displays actual allocations, provisional status, conditional readiness and reconciliation warnings. Weekly displays current plan version, solver/checker states, source freshness, task queue, chart, resource timeline and contextual evidence drawer. Keep the chart dominant and readable at 1280/1440/1920 widths; use an overlay drawer when docking would crush it.

Use ECharts for time-distance and resource views. Time is horizontal, station/chainage vertical, with explicit direction/track identity and Asia/Kolkata labels. Draw train trajectories only when real input path samples support them; otherwise draw truthful occupation bands. Maintenance bands represent complete affected occupation, not only productive work. Render setup/work/testing/restoration detail from materialized phases. Do not silently omit an electrical or route footprint to make the diagram look clean.

Selection synchronizes task row, chart highlight, resource usage and evidence. Provide visible zoom/pan/reset, filters, legend, keyboard-accessible equivalents and a tabular schedule. Filters change visualization only, never solver constraints. Keep long IDs/source timestamps in useful details rather than flooding the main view. Use explicit TEST/provisional/stale/locked badges with text and shape.

Wire actual Generate plan, run status, cancellation, version selection, task edits and parent-reconciliation navigation. Edits create revisions and require recomputation. Until safe server-validated drag-to-propose exists, use a clear edit form and omit misleading drag affordances. Show no-run empty state, running state, infeasible diagnostics, timeout/UNKNOWN, FEASIBLE-not-optimal, invalid checker result and stale applicability without faking success.

Capture and inspect browser screenshots of monthly allocation, populated weekly chart with open evidence, infeasible state and compact review view. Test a reload, navigation back, stale query cache and long data values. Ensure visible keyboard focus, readable contrast, source labels and no body-wide overflow.

Acceptance: a user can log in, inspect/edit actual inputs, launch a real solve, view the checked result and inspect its tasks/resources/source lineage. Screenshot beauty does not substitute for this end-to-end browser test. No Math.random-generated chart series, canned metrics or disconnected mock service may remain on release routes.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-11.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
