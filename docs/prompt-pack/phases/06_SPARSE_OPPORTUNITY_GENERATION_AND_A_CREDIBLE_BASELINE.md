# Phase 06 - Sparse opportunity generation and a credible baseline

Copy-ready implementation prompt. Run after: 04-05.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 19, 22, 37-39, 42.

Implement candidate generation and a coordinated greedy baseline before CP-SAT integration.

A candidate fixes a package/recipe, allowed window, start, resource assignment and full materialized phases. Use UTC integer seconds with a declared 60-second start lattice; preserve original timestamps for the checker. Round unavailable intervals outward and eligible windows inward when discretizing. This resolution is not a Railway safety buffer. Unknown required facts make candidates ineligible with evidence.

Check window containment including restoration, train/fixed occupation, topology, deadlines/releases, resources/competence/travel, readiness, dependencies, compatibility and commitments. Build indexes by affected resource and relevant time range. Do not compare every candidate with every other candidate globally. Measure candidate construction time, peak memory, counts before/after pruning, conflict-edge count and rejection categories separately from later solver runtime.

Generate safe singletons and locality-filtered pair/triple packages. Prune only on a documented sound infeasibility or dominance rule. Make caps deterministic, configurable and part of CandidateManifest. If a cap is hit, return DOMAIN_TRUNCATED, not a misleading complete-domain result. Preserve evidence of omitted search scope; missing candidates cannot prove physical infeasibility. Initial weekly 20,000 and monthly 50,000 limits are proposed guardrails, not benchmarks. Include an expansion mechanism only if bounded and versioned.

Implement mandatory-first, authorized-tier/deadline-priority greedy planning on the same candidates, with compatible grouping and one bounded repair pass. Preserve commitments and avoid duplicate task coverage. Failure to find mandatory coverage is BASELINE_NO_FEASIBLE_PLAN_FOUND, not proof the underlying problem is infeasible. Do not deliberately weaken the baseline to inflate gains.

Provide a developer CLI or test harness producing serialized candidate manifests, baseline assignments and diagnostic artifacts from actual snapshots. The independent checker arrives in Phase 07; until it passes, label baseline results unchecked and non-publishable.

Acceptance: hand-checkable candidate sets; cross-midnight containment; exact boundary handling; pair/triple domain limits; no non-local quadratic conflict scan; deterministic manifest on equivalent inputs; no-benefit scenario; baseline can coordinate a known package. Record real measurements for 10 and 30 task cases with different window/resource densities. Do not conclude scalability from task count alone.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-06.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
