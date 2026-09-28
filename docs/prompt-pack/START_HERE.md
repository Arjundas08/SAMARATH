# SAMARATH implementation prompt pack

Version 1.0 | Prepared 26 September 2026 | Team NIRVIKALP | SIH26027

This pack contains **25 copy-ready prompts**: one master prompt, 20 core implementation phases (00-19), two separately gated future phases (20-21), a resume prompt and a focused regression-repair prompt. It also includes the detailed frontend design brief, explicit changes to the original implementation priorities, and the reviewed 98-page blueprint.

These are implementation instructions to use with a coding agent in your chosen application repository. This delivery does not implement the application, train a model or establish production readiness. A strong prompt cannot replace passing correctness, usability and domain-validation gates.

## Start here

1. Create/open the folder intended for the SAMARATH application. Keep the prompt-pack folder inside it, for example docs/prompt-pack/. If an application already exists, open that repository and preserve its code. Do not accidentally use the old report-generation workspace as the application repository.
2. Keep the whole pack accessible to the coding agent. Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md and DESIGN_BRIEF.md once yourself.
3. Send the starter instruction below. Phase 00 inspects the repository and freezes contracts; Phase 01 produces the runnable scaffold.
4. Run **one phase prompt at a time** in numerical order. Prefer one continuing implementation task. Do not paste the entire combined collection and ask for everything in a single pass.
5. Review the phase report and actual evidence before advancing. A scaffold or screenshot is not a passed planning gate. If blocked, use the resume or focused repair prompt after resolving the dependency.
6. In a new conversation, ask the agent to reread the master, addendum, design brief, state and relevant phase. Do not rely on remembered context or paste only an isolated fragment of a phase.
7. Optional pilot/ML phases require a separate request and their real data/authorization prerequisites. They are not part of the default build sequence.

## Copy this starter instruction

Read the SAMARATH prompt pack's MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and START_HERE.md. Inspect this application's repository and applicable AGENTS.md instructions. Then execute only the complete Phase 00 prompt under phases/. Preserve existing work. Create the implementation state and acceptance matrix, resolve the documented scope and contract decisions, and report actual evidence and missing prerequisites. Do not start Phase 01 automatically and do not claim an application has been built during the audit phase.

## How to continue after a passed phase

Read docs/IMPLEMENTATION_STATE.md and the previous phase report. Confirm its prerequisite gates from code and test evidence. Then read and execute the complete next numbered prompt from the SAMARATH prompt pack's phases/ folder, following the master prompt, implementation addendum and frontend design brief. Finish its acceptance checks and update state before stopping. Do not replace real results with mocks to pass a gate.

## Phase map

| Phase | Outcome | Prerequisites |
|---|---|---|
| 00 | [Repository audit and implementation contract](phases/00_REPOSITORY_AUDIT_AND_IMPLEMENTATION_CONTRACT.md) | None |
| 01 | [Runnable foundation, database and typed contracts](phases/01_RUNNABLE_FOUNDATION_DATABASE_AND_TYPED_CONTRACTS.md) | 00 |
| 02 | [Real login, scoped permissions and secure sessions](phases/02_REAL_LOGIN_SCOPED_PERMISSIONS_AND_SECURE_SESSIONS.md) | 01 |
| 03 | [Distinctive design system and honest application shell](phases/03_DISTINCTIVE_DESIGN_SYSTEM_AND_HONEST_APPLICATION_SHELL.md) | 01-02 |
| 04 | [Input gateway, fictional corridor and provenance](phases/04_INPUT_GATEWAY_FICTIONAL_CORRIDOR_AND_PROVENANCE.md) | 01-03 |
| 05 | [Readiness, compatibility and executable work packages](phases/05_READINESS_COMPATIBILITY_AND_EXECUTABLE_WORK_PACKAGES.md) | 04 |
| 06 | [Sparse opportunity generation and a credible baseline](phases/06_SPARSE_OPPORTUNITY_GENERATION_AND_A_CREDIBLE_BASELINE.md) | 04-05 |
| 07 | [Independent feasibility checker and correctness oracle](phases/07_INDEPENDENT_FEASIBILITY_CHECKER_AND_CORRECTNESS_ORACLE.md) | 05-06 |
| 08 | [Real CP-SAT weekly optimizer and objective profiles](phases/08_REAL_CP_SAT_WEEKLY_OPTIMIZER_AND_OBJECTIVE_PROFILES.md) | 06-07 |
| 09 | [Monthly allocation and weekly reconciliation](phases/09_MONTHLY_ALLOCATION_AND_WEEKLY_RECONCILIATION.md) | 08 |
| 10 | [Durable solve jobs and complete planning APIs](phases/10_DURABLE_SOLVE_JOBS_AND_COMPLETE_PLANNING_APIS.md) | 02, 08-09 |
| 11 | [Beautiful operational planning workbench](phases/11_BEAUTIFUL_OPERATIONAL_PLANNING_WORKBENCH.md) | 03-05, 09-10 |
| 12 | [Evidence-backed Why, Why-Not and bounded repair](phases/12_EVIDENCE_BACKED_WHY_WHY_NOT_AND_BOUNDED_REPAIR.md) | 07-11 |
| 13 | [Event-driven stable replanning and PlanDiff](phases/13_EVENT_DRIVEN_STABLE_REPLANNING_AND_PLANDIFF.md) | 09-12 |
| 14 | [Calculated metrics, fair comparison and stress scenarios](phases/14_CALCULATED_METRICS_FAIR_COMPARISON_AND_STRESS_SCENARIOS.md) | 08-13 |
| 15 | [Human review, programme approval and audit integrity](phases/15_HUMAN_REVIEW_PROGRAMME_APPROVAL_AND_AUDIT_INTEGRITY.md) | 02, 09-14 |
| 16 | [Execution feedback, partial work and estimate review](phases/16_EXECUTION_FEEDBACK_PARTIAL_WORK_AND_ESTIMATE_REVIEW.md) | 04, 13, 15 |
| 17 | [Failure recovery, security and scaling evidence](phases/17_FAILURE_RECOVERY_SECURITY_AND_SCALING_EVIDENCE.md) | 00-16 |
| 18 | [Final visual craftsmanship and accessibility pass](phases/18_FINAL_VISUAL_CRAFTSMANSHIP_AND_ACCESSIBILITY_PASS.md) | 11-17 |
| 19 | [Release rehearsal, judge challenge and handover](phases/19_RELEASE_REHEARSAL_JUDGE_CHALLENGE_AND_HANDOVER.md) | 00-18 complete with evidence |

## What the agent should show after every phase

- Working behavior and relevant changed files.
- Actual commands and test results, with NOT_RUN clearly labelled.
- Browser evidence for UI phases and raw measurements for performance phases.
- Remaining defects/dependencies and the updated acceptance/state records.
- The next eligible phase, without silently starting it.

## Frontend expectations

The visual direction is Signal & Slate: ink-blue navigation, light work surfaces, precise railway time-distance graphics, restrained teal interaction, clear disruption accents and a contextual evidence drawer. It is designed as an operator's planning workbench. Phases 03, 11 and 18 cover its foundation, real-data interaction and final visual/browser/accessibility review. DESIGN_BRIEF.md provides tokens, layout, all eight workspaces, chart semantics, responsive states and screenshot acceptance scenes.

A beautiful static dashboard is insufficient. The release must support login, input revisions, real solve/check, evidence, live changes, calculated comparisons and human review. The chart cannot draw train movement that its input records do not support.

## Material improvements over blueprint v1.0

The addendum makes scope, sparse candidate generation, two replanning objective profiles and real monthly/weekly reconciliation explicit. Recovery prioritizes fewer changes after protecting hard obligations and required coverage; it is not allowed to reshuffle a programme for a marginal efficiency gain. Scalability remains a measured gate. The original PDF is preserved unchanged for traceability.

## Contents and useful files

- MASTER_PROMPT.md: project-wide implementation contract.
- IMPLEMENTATION_ADDENDUM.md: proposed v1.1 refinements from the feasibility review.
- DESIGN_BRIEF.md: detailed frontend art direction and behavior.
- ALL_PROMPTS.md: one searchable combined document containing the master, addendum, design brief and every prompt.
- phases/: the 20 core prompts, ready to copy or ask the agent to read.
- optional/: authorized Railway shadow pilot and historical-data ML prompts.
- utilities/: resume and focused regression repair prompts.
- references/: original blueprint in Markdown/PDF and its PlantUML assets.
- REVIEW_NOTES.md: what was reviewed and what remains unverified.
- MANIFEST.json: file inventory and integrity hashes.

No fixed completion date, competitive outcome or speedup is promised. The benchmark must distinguish generation, model construction, solving and independent checking. A phase that cannot demonstrate its gate is unfinished, regardless of how polished its description sounds.
