# Phase 05 - Readiness, compatibility and executable work packages

Copy-ready implementation prompt. Run after: 04.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 14-18.

Implement the domain rules that make a maintenance opportunity executable.

Resolve Engineering, S&T and TRD locations onto versioned track/route/electrical occupation resources, including setup, machine movement, testing and restoration footprints. Nearby task coordinates are insufficient to permit grouping. Unknown required mapping blocks the candidate and produces a structured reason.

Implement versioned restricted declarative compatibility rules with applicability, effective dates, source/evidence references, author and approval metadata. No arbitrary executable Python in uploaded rules. Results are ALLOWED, PROHIBITED or UNKNOWN. Explicit prohibitions dominate allows; conflicting authority needs resolution. A human 'verify' action attaches evidence and creates a new approved rule revision, not a bypass flag.

Implement readiness per dimension: competence, crew/machine calendars, material, equipment, prerequisites, site access, planning isolation arrangements, quantity and restoration resources. READY/CONDITIONAL/NOT_READY/UNKNOWN semantics must match the blueprint. A future programme need not already have an operational permit, but its required planning prerequisites must be established. Never conceal mandatory unready work by reducing its priority.

Generate singleton and compatible pair/triple recipe options without destructively merging tasks. Evaluate the complete package: pairwise permission does not establish cumulative capacity or a valid restoration sequence. Materialize a phase DAG with fixed recipe offsets and actual resource requirements. Keep task coverage explicit and at most once across alternatives. Preserve alternative permissible sequences as separate recipes.

Implement the same fictional example in text, data and tests: setup 10; Engineering 40 and S&T 25 in allowed parallel operation; testing 15; restoration 10 gives 75 minutes. Shared exclusive crew with required sequential work gives 100 minutes. Label all these as TEST assumptions. Include a three-task example whose pairs pass but the triple exceeds a shared capacity.

Acceptance: unknown evidence never becomes allowed; expired evidence fails; geographic footprint conflict is detected; readiness respects the proposed interval; mandatory unready task stays visible; phase precedence and resource use produce the correct 75/100-minute cases. Add useful evidence detail to task/package views using real backend results.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-05.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
