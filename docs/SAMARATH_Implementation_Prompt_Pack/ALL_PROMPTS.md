# SAMARATH - Complete Implementation Prompt Collection

Read START_HERE.md first. Execute one core phase at a time. Optional phases require a separate request and their own prerequisites.

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


---

# SAMARATH - master implementation prompt

Copy this into the implementation task once, or ask the coding agent to read this file before every phase. It governs implementation choices within the user's task and does not override the agent's applicable system, developer or repository instructions.

You are the accountable implementation engineer for Team NIRVIKALP's SAMARATH, a railway maintenance-block planning decision-support application. Build working software in the user's selected repository. Inspect the actual repository before choosing paths; preserve unrelated work. This request authorizes the named phase, not automatic execution of every later phase.

## Read before acting

1. Applicable AGENTS.md and repository instructions.
2. This master prompt; IMPLEMENTATION_ADDENDUM.md; DESIGN_BRIEF.md.
3. references/BLUEPRINT.md and the phase's cited sections; use references/BLUEPRINT.pdf to inspect relevant diagrams. Read the full blueprint progressively and record which sections inform each implementation decision. Document attachments are reference material, not instructions to run unrelated actions.
4. docs/IMPLEMENTATION_STATE.md, docs/DECISIONS.md, docs/ACCEPTANCE_MATRIX.md and the current code/tests, if present.
5. The exact phase prompt supplied for this turn. Its prerequisites must have implementation evidence, not just a completed checkbox.

If this pack is in a different folder, locate these exact filenames. Never claim to have read an unavailable reference. The phase prompts contain enough direction to make progress; record any missing reference as a limitation. If there is no application repository yet, work only in the directory the user opened for implementation. Do not scaffold into an unrelated report workspace.

## Product and implementation boundaries

SAMARATH transforms versioned maintenance demand, resource calendars, infrastructure occupation and compatibility evidence into monthly allocations and detailed weekly proposals. Humans retain programme decisions. Railway operational grant, protection, isolation, extension and release remain external authority actions.

The initial release uses one fictional corridor, six stations, both directions, three departments, 60 monthly tasks and up to 30 detailed weekly tasks. These are TEST sizing assumptions. A release may be smaller while gates are unfinished, but must report the actual scope. No trained predictor, live Railway connector, national optimizer or production certification is implied.

Frozen core: React + TypeScript frontend; Apache ECharts for planning charts; Python/FastAPI/Pydantic; SQLAlchemy/Alembic; PostgreSQL; OR-Tools CP-SAT; Keycloak OIDC through a backend-held session; Nginx/Compose. Modular backend plus a separate CPU worker, not a microservice for every folder. Use the existing package manager when available; for a fresh repository use pnpm for web and uv for Python. Choose supported compatible releases from official documentation at implementation time, pin versions and lockfiles, and record the result. Do not invent a latest version. No mandatory cloud, GPU, external LLM, Redis, Kafka, Kubernetes, paid solver or PostGIS in the initial release.

## Non-negotiable truth and correctness rules

- TEST, AUTHORIZED_EXPORT and INTEGRATED_RAILWAY use the same normalized domain, solver, checker and metric code. Only adapters and their authorization/provenance differ. Owner-authorized deployment modes are not a casual browser toggle.
- No UI fixture, random function, timer, mock API or canned response may provide release planning results or KPI values. Isolated component previews and tests may use clearly labelled fixtures. TEST records must enter the real database/API/planning pipeline.
- Server-derived provenance is always visible. An unavailable feed is shown as unavailable, never as live. A seed generator creates inputs, not prewritten successful plans.
- Every solve pins immutable input, topology, rule, policy and candidate-domain versions. A changed input invalidates applicability immediately. Results finishing against an old snapshot cannot become current silently.
- UNKNOWN required compatibility/evidence never becomes ALLOWED. No invented Railway-specific buffer, local safety rule, productivity norm or official designation. Fictional rules are marked TEST_RULE; real applicability requires owner evidence.
- Mandatory work and applicable protection are hard constraints. A diagnostic relaxation is non-publishable. Completed work and operational reservations are never automatically unlocked. Missing release observations do not free occupied infrastructure.
- Package duration comes from setup/work/testing/restoration phases, resource calendars and an approved concurrency recipe. It is not automatically the maximum task duration.
- The validator re-evaluates original-resolution inputs and assignments independently. It cannot call optimizer/candidate feasibility predicates or trust their flags. Shared schemas are permitted; separate checker logic and mutation tests are required.
- Distinguish solver status, stop reason, checker verdict, domain completeness, applicability and approval eligibility. FEASIBLE is not OPTIMAL. UNKNOWN is not proven infeasible. A solver result alone does not make a proposal approvable.
- All metrics are calculated from a persisted snapshot and result version. Zero denominators yield N/A with a reason. Fewer completed tasks must not masquerade as availability improvement.
- Structured evidence drives Why/Why-Not. Do not invent causal explanations, probability claims or an LLM-generated authority statement.
- No autonomous grant/extension/release endpoint. The external authority mirror is read-only to ordinary planning actions. Programme approval is distinct from operational permission.

## Work discipline

Implement the requested phase rather than stopping at a plan or code suggestions. Make ordinary reversible choices without repeated confirmation. A missing Railway fact becomes an explicit unknown or blocked capability; do not guess it. Ask only when missing information truly prevents safe progress, and continue independent work where possible.

Inspect before replacing. Prefer small modules and typed contracts. Avoid broad rewrites, speculative abstractions, duplicate state stores and adding tools for appearances. Avoid editing generated API clients by hand. The default UI has no fake integrations, dead actions, promotional landing page or decorative dashboard metrics.

Do not weaken tests to obtain a pass. Use targeted tests that exercise real behavior, then relevant integration/browser checks. Never claim a test, screenshot, benchmark, restore or security check ran when it did not. If an environment dependency prevents execution, label that gate NOT_RUN and explain the exact blocker. Never label the phase complete on that evidence.

Use additive/compatible migrations and test rollback where practical. Do not delete user data, reset a shared database, expose secrets, publish, push or deploy externally as an incidental part of a phase. Keep supplied Railway material out of public commits and logs. Use environment templates without real credentials.

## Continuity and completion contract

Maintain docs/IMPLEMENTATION_STATE.md with: current phase, COMPLETE/PARTIAL/BLOCKED/NOT_RUN gates; implemented capabilities; actual commands/results; changed contracts/migrations; known defects; next prerequisite. Keep a traceable acceptance matrix linking each requirement to code, tests and evidence. Each phase writes docs/phase-reports/PHASE-NN.md. Store screenshots and benchmark data under artifacts with versions and dates; do not overwrite baselines casually.

A phase ends only after its acceptance criteria pass or the remaining blocker is clearly documented. Return: what works now; how to run/reproduce it; checks actually run and results; material limitations; and the next eligible phase. Update state before stopping. Do not automatically start the next phase or claim the project is complete after a scaffold.

When resuming, inspect the state and actual repository. Preserve completed work and reproduce the reported failure before changing it. A polished UI, a compile-successful build and a working planning system are three different gates.


---

# Implementation addendum v1.1 - 26 September 2026

This pack was prepared after reviewing the generated 98-page blueprint and the subsequent feasibility assessment. It is a proposed implementation refinement. The original blueprint v1.0 remains unchanged; this addendum makes the following decisions explicit for the implementation prompts.

1. Build a bounded, demonstrable vertical slice before expanding the blueprint's large MUST list. Every listed core capability still has a delivery phase; a partial build must not be presented as the finished release.
2. Two objective profiles: PROGRAMME_IMPROVEMENT follows feasibility, mandatory work, authorized priority tiers/soft deadlines, occupation/declared operating proxy, then stability and mobilization. DISRUPTION_RECOVERY preserves hard obligations and commitments, protects required/critical coverage, and prioritizes fewer changes before marginal efficiency improvements. An explicit coverage floor and authorized priority policy prevent preserving routine assignments at the expense of required work. Version the exact lexicographic ordering in an ADR and tests. Never change it invisibly between runs.
3. Benchmark candidate construction and model size early. The 20,000-weekly-placement limit is an unvalidated guardrail, not demonstrated capacity. A naive all-pairs scan at that size examines 199,990,000 pairs. Use resource/time indexes and sparse conflict generation. If a bounded domain truncates, disclose it; do not imply complete physical-problem infeasibility.
4. Keep CP-SAT as primary, but allow a documented, correctness-tested representation change if profiling favors interval constraints or another CP-SAT encoding. Avoid building two production solvers. Tiny exhaustive cases are the comparison oracle.
5. Monthly allocation is provisional. Build actual parent-child reconciliation, not just two calendar screens. Enough aggregate hours do not establish minute-level feasibility.
6. The judge-facing strength is evidence-aware packages, precise rejection/repair, and stable response to a changed input. Frontend design serves those decisions.
7. Trained ML and real Railway integration remain gated. Current official AI/ML expectations and 2026 competition rules need confirmation; no unsupported eligibility or scoring claim is embedded in these prompts. Prototype use of CP-SAT must be called optimization, not a trained predictor.
8. No fixed timeline, winning probability or measured speedup is promised. Candidate/model/solver/checker latency and correctness must be measured on stated hardware.
9. Initial UI: seven navigation destinations with an evidence drawer, preserving the blueprint's eight workspaces without a redundant separate evidence page. Departments are filters/permissions, not duplicated products. Desktop planning is primary; compact screens support usable review and forms.
10. Design is built early and verified again after real data integration. Skeleton states and isolated component fixtures may be designed early; release figures and interactions must be backed by actual services.

## Release gates

G0: consistent contracts and development setup (00-02).
G1: labelled source inputs, geometry, rules, baseline and independent checking (03-07).
G2: real monthly/weekly solve exposed through durable APIs and rendered in the workbench (08-11).
G3: reasons, bounded repair, stable replanning, measured comparison and review/feedback (12-16).
G4: failure/security/performance evidence, visual/browser QA and reproducible offline release (17-19).

Phases 20-21 are separate optional pilot/ML work and are not authorized by completing the hackathon release. The guide supplies prompts for them so the path is explicit; execute them only when their prerequisites and user request exist.


---

# SAMARATH frontend design brief - Signal & Slate

The desired result is a distinctive, polished railway planning workbench: calm, precise, spacious where decisions need attention, and dense where operators compare records. Beauty should come from typography, alignment, strong information hierarchy and excellent interaction. Do not claim an objectively 'best in the world' interface; demonstrate quality through rendered screens and task performance.

## Art direction

Use an ink-blue navigation frame, warm light work surfaces, crisp rules, restrained teal selections and functional orange disruption accents. Railway identity comes from time-distance paths, chainage rulers, possession bands, direction markers and phase sequences. Avoid stock train photographs, invented government seals, neon cyberpunk styling, glassmorphism, giant gradient headers and interchangeable KPI-card grids.

Create an original simple inline-SVG SAMARATH mark from parallel tracks and one controlled branching path. Keep the name SAMARATH prominent with Team NIRVIKALP secondary. Do not imply official Indian Railways branding or endorsement. SVG is suitable; image generation is unnecessary for the operational interface.

Starter tokens, subject to measured contrast validation:
- Canvas #F4F6F8; surface #FFFFFF; warm surface #FAF9F6.
- Ink #142B3E; muted text #526478; border #D5DEE5.
- Action/selection #006D77; tint #E6F2F2.
- Warning #946200 with a pale warm background; critical #B33636; change accent #B94D2F.
- Success, UNKNOWN, STALE, BLOCKED, TEST and AUTHORIZED states each require explicit text/icon semantics, never colour alone.
- A measured 4/8-pixel spacing system; 6-10 pixel control radii; fine borders; subtle shadow only for overlays and hierarchy. Avoid excessive rounded containers.

Use locally hosted, licence-appropriate fonts: one readable sans family (prefer Inter if available and licensed) with system fallback, plus a monospace family for times/IDs. Use tabular numerals. Typical body 14-16px; table text 13-14px; headings 20-28px; diagram labels at least 12px where possible. Do not hide critical facts in tiny text. Font downloads must not be required at demo runtime. Record licence notices if bundled.

Choose a coherent CSS token system and accessible headless primitives. Keep the component library minimal; style the application intentionally. Prefer the repository's existing approach if sound. For a fresh build, CSS variables with component styles and accessible React primitives are sufficient; a second styling framework is unnecessary. Keep ECharts as the planning visualization library, with bespoke render functions when needed.

## Navigation and layout

Seven destinations: Overview, Maintenance, Planning, Change Review, Rules & Readiness, Data & Outcomes, Audit. The Evidence Drawer is the eighth workspace and opens contextually from several destinations. Monthly/Weekly, Time-Distance/Resources and Current/Compare are subordinate views, not separate top-level apps.

Persistent top context: corridor/territory, selected horizon, data provenance, source age, snapshot/plan version and user role. Keep technical IDs in a details disclosure except where they support a comparison or audit decision. Never place infrastructure terms such as 'CP-SAT job lease' in an ordinary planner action. Prefer 'Generate plan', 'Review changes', 'Why not scheduled?' and 'Check data freshness'.

Desktop planning layout: collapsible global navigation, a 240-280px maintenance queue, a dominant chart workspace and a contextual 360-400px evidence drawer. Dock the drawer only when the chart remains genuinely usable; otherwise use a dismissible overlay. At wide widths the navigation can collapse to a narrow rail to preserve chart area. Avoid rigid columns that crush the chart at 1280px.

Desktop targets: 1280x800, 1440x900 and 1920x1080. At 768px support coherent tablet review and forms. At 390px retain navigation, task detail, evidence, source warnings and review actions. Complex timeline editing may switch to an accessible list/detail view with explicit zoom controls. Horizontal scrolling is intentional inside a time axis, not across the entire page. No hidden unreachable action at 200% zoom.

## Screen responsibilities

1. Overview: an operational briefing. Show current planning applicability, mandatory work needing attention, input-quality blockers, latest completed run, and a compact corridor/horizon summary. Use computed values only. Before a run exists show an informative empty state with import/plan actions, not zero-valued fake success cards.
2. Maintenance: search/filterable table with department, asset/chainage, due time, criticality, readiness and source age. Expand a row into requirements and evidence. Batch actions must respect roles and validate each task; never silently rewrite imported source records. Forms show units and error locations.
3. Planning: the hero workbench. Monthly view emphasizes week allocations and resource-pressure bands. Weekly view emphasizes train occupation, maintenance proposals, resource constraints and selected work phases. Solve controls show genuine queued/running/checking/completed/failed/cancelled states. A spinner never invents percentage progress.
4. Evidence Drawer: selected package/tasks, phase durations, consumed resources, rule/source references, readiness, checks, Why and Why-Not. Keep observed facts, optimization tradeoffs and uncertainty visually distinct. Offer a permitted repair only if a stored trial supports it.
5. Change Review: old/new versions with synchronized time ranges, textual PlanDiff, preserved/conflicting locks, baseline metrics with denominators, and review/approval controls. Comparison must remain understandable without colour. Explain every disabled approval condition with a route to resolve it.
6. Rules & Readiness: effective rule versions, applicability, evidence, pending verification and resource/calendar requirements. Give UNKNOWN a proper workflow, not a decorative amber badge. Rule authors and approvers have separate actions.
7. Data & Outcomes: import manifest, accepted/quarantined rows, exact validation errors, source age, connector entitlement and actual execution feedback. External authority observations are read-only. A TEST badge stays visible throughout the workflow.
8. Audit: searchable version/event/decision history and reproducible run details with correlation IDs, role and source references. Displaying history must not imply every database administrator is technically unable to alter data.

## The signature planning visualization

Time on x; station/chainage on y; label Asia/Kolkata and the displayed dates. Show UP/DOWN or track identity explicitly. Train paths require actual route/time samples; if only occupancy intervals exist, draw occupancy bands and state that continuous train trajectories are unavailable. Never interpolate fictitious train movement as observed data.

Maintenance bands encode requested/selected windows and the true affected footprint. Use patterned or outlined treatments for provisional, stale, locked and unknown states. Planned infrastructure unavailability is distinct from a work task's productive time. Phase detail separates setup, work, testing and restoration. Resource timelines occupy a linked secondary panel or tab; do not confuse resource identity with kilometre distance.

Selecting an assignment highlights its affected resources and opens the drawer. Hover offers concise facts; all content is also reachable through keyboard focus and the accessible table. Zoom/pan has visible controls, reset and a preserved selection. Train/background visibility filters cannot change the constraints used by the solver.

Dragging work creates an explicit proposed input/lock revision, validates it and requests a fresh solve. It never mutates an approved immutable plan in the browser. If safe drag behavior is not implemented, provide a clear edit form and omit the drag affordance. No visually draggable object that silently snaps back without explanation.

## Interaction and state quality

Every important route must support loading, empty, partial data, rejected import, UNKNOWN rule, stale result, forbidden action, infeasible solve, timeout without incumbent, feasible non-optimal result, server outage and successful recovery. Preserve user input after a retryable error. Prevent duplicate submissions with real idempotency and button state. Disabling a button is not authorization.

Use 120-200ms restrained transitions for drawer/menu/selection changes, with reduced-motion support. Do not animate a schedule into a different assignment before a verified new result arrives. Respect focus on rerenders; return focus after dialogs. Keyboard navigation, labelled controls, clear focus rings, semantic headings and accessible status announcements are required. Target WCAG 2.2 AA and verify contrast/focus/zoom with actual checks; do not claim certification.

Use optimistic updates only for reversible UI preferences or draft inputs with rollback. Planning results, locks, approvals, authority observations and metric values require server confirmation. Store filter/selection state without persisting secrets or auth tokens in localStorage.

## Visual QA and deliverables

Maintain a component gallery restricted to development/test builds with visible fixtures. Capture browser screenshots from implemented screens using the real local API and TEST database. Required scenes: empty first use; populated maintenance queue; monthly allocation; weekly plan with an open evidence drawer; infeasible input; new event while solving; PlanDiff; stale/blocked approval; quarantined import; compact mobile evidence view.

Review alignment, chart labels, text density, white space, selected-state contrast, clipping, focus, long IDs and names, empty tables, 200% zoom and reduced motion. Fix observed defects rather than merely producing screenshots. Keep screenshot baselines tied to fixture and application versions. Do not substitute image-generation mockups for working UI evidence.

The visual success test: in a populated workbench, a new viewer can identify the corridor, horizon, data mode, proposed maintenance and current issue within 10 seconds; a planner can inspect the blocking evidence and next permitted action without navigating through several unrelated pages. These are proposed usability checks, not measured results.


---

# Phase 00 - Repository audit and implementation contract

Copy-ready implementation prompt. Run after: None.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 1-9, 29-33, 44-48.

Implement Phase 00 only. Establish an executable development plan grounded in this repository; do not generate the whole application yet.

Inspect the working tree, existing services, migrations, tests, dependency files and local instructions. Identify useful code to preserve. If no application exists, define the monorepo layout from the blueprint with one Python package graph; actual scaffolding is Phase 01. Read the blueprint, addendum and frontend design brief. Summarize any contradictions with the current code and resolve routine implementation choices through documented ADRs.

Create docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md, docs/DECISIONS.md, docs/SCOPE.md and docs/API_CONTRACT.md. Map the 20 core phases to requirement IDs, owner skill, prerequisites, evidence and exit gates. Mark every capability as existing-and-tested, existing-unverified, missing or deferred. Do not mark an unimplemented capability as done because its design is written.

Freeze the bounded TEST corridor scope, units, UTC storage/Asia-Kolkata display, immutable revision strategy, three data modes and separate demand/programme/authority states. Define the exact two objective profiles from the addendum, including coverage protection before stability in recovery mode. Freeze API names around the blueprint; add explicit CRUD/revision contracts for resource calendars, train occupations, windows and topology needed for arbitrary evaluator edits. Do not invent external Railway endpoints.

Specify source-of-truth contracts for Task, Snapshot, CandidateManifest, MaterializedAssignment, SolverRun, ValidationResult, PlanVersion, Reason, PlanDiff and PlanMetric. Include run/snapshot/version relationships, status enums and structured errors. Define which fields are server-derived. Record the expected database ownership and validator import boundary.

Review current official dependency documentation only where needed to select mutually compatible supported versions; record sources and pinning plan. Define canonical commands for install, migrate, seed, run API/web/worker, unit/integration/browser tests and production build. Flag environment gaps honestly. Do not train ML or claim SIH rule confirmation from the older guideline.

Acceptance: every phase has an unambiguous gate; no competing versions of the same API contract; all unresolved Railway facts are explicit; the implementation state matches inspected code. Return the first runnable phase and any real blocker. This phase produces project-control documents, not a claim of a working prototype.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-00.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.


---

# Phase 01 - Runnable foundation, database and typed contracts

Copy-ready implementation prompt. Run after: 00.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 11-13, 29, 31, 43, 47.

Implement a clean runnable foundation in the existing repository, preserving unrelated work.

Create apps/web, apps/api, the modular Python packages, workers, adapters, db/migrations, scenarios, tests and infra only as needed. Wire React/TypeScript, FastAPI, PostgreSQL and Compose with pinned dependencies and lockfiles. Keep CPU planning work out of request handlers. Provide .env.example without real secrets, health/readiness checks, structured logs, developer instructions and reproducible commands. Health must distinguish a reachable process from a usable database.

Implement initial migrations for identities/scopes, sources/connectors, revision envelopes, topology resources/mappings, maintenance tasks/requirements, calendars, windows, train occupation, snapshots/membership, policy versions, jobs/outbox, run/result skeletons and audit events. Add detailed business tables in later phases through migrations. Document how every blueprint entity is implemented, grouped or deferred. Do not create dozens of empty repositories merely to mirror an entity list.

Every versioned record has stable identity and immutable revision identity, provenance and territory scope. Use database keys, uniqueness and check constraints for required invariants; prevent snapshot references to mutable content. Use integer seconds/metres and typed units. Define canonical serialization and stable hashing of snapshots with sorted membership, explicit timestamp representation and versioned schemas; never hash an unordered mutable JSON object opportunistically.

Create Pydantic contracts and generate a TypeScript API client/types from OpenAPI. Define enums independently for job state, solver status, stop reason, domain completeness, validation, applicability, provenance and approval eligibility. Reject unexpected enum values and invalid units. No fabricated successful solver endpoint.

Test migrations on an empty disposable PostgreSQL database and a representative upgrade; verify revision uniqueness, FK integrity, stable snapshot hash under equivalent ordering, changed hash on actual content revision, and schema/client generation. Use PostgreSQL for DB integration tests rather than substituting SQLite semantics. Include smoke checks for API/web startup and a production frontend build.

Acceptance: documented commands reproduce the scaffold; real PostgreSQL persistence works; migrations and typed contracts pass their targeted checks; service unavailability is visible. Solver and integration capabilities are explicitly unimplemented.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-01.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.


---

# Phase 02 - Real login, scoped permissions and secure sessions

Copy-ready implementation prompt. Run after: 01.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 8-9, 31, 33-34.

Implement real local identity and authorization before adding business write actions.

Use Keycloak OIDC authorization-code flow with PKCE, state/nonce and backend token handling. Browser uses an HttpOnly, Secure, appropriate SameSite session cookie through a same-origin proxy; do not put tokens in localStorage. Validate issuer, audience, signature, expiry and callback state. Implement login, logout, session expiry and rotation using maintained libraries. Document local TLS setup and any explicit localhost-only development exception; no demo bypass must survive a release configuration.

Seed fictional functional roles: departmental planners, coordinator, operating reviewer, delegated programme approver, integration operator, rule author/approver, auditor and infrastructure administrator. Use permissions plus department and territory scopes; infrastructure administrator is not automatically a business approver. Model explicit scope grants for shared boundary resources. Never trust role/territory/mode sent from the client.

Implement GET /api/v1/session and authorization dependencies for API/domain actions. Enforce row access in services and add PostgreSQL RLS where designed, with a non-owner/non-bypass app role. Ensure connection-pool reuse cannot leak another request's scope: use transaction-local settings and test cleanup. Workers must operate on authorized scoped jobs rather than granting themselves global business access.

Add CSRF protection to cookie-authenticated mutations, constrained CORS, session limits and redacted authentication logs. Separate credentials for migration, API and worker as appropriate. Keep TEST bootstrap users local and clearly documented; no production default password. Do not expose client secrets in frontend assets.

Acceptance tests: successful login and logout; expired session; invalid callback state; unauthenticated 401; forbidden role action; cross-territory access with no record disclosure; forbidden cross-department mutation; administrator cannot approve; connection reuse does not cross scopes. Browser tests must use real local authentication, not a mocked role dropdown. Return permission matrix and actual test evidence.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-02.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.


---

# Phase 03 - Distinctive design system and honest application shell

Copy-ready implementation prompt. Run after: 01-02.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 32 and DESIGN_BRIEF.md.

Implement the first frontend design pass using the Signal & Slate brief. Build an intentional railway planning interface, not a template dashboard.

Create design tokens, typography, density, focus, spacing, borders, semantic status treatments and an original simple SVG SAMARATH mark. Use accessible primitives and one coherent styling system. Bundle licensed fonts locally or use reliable system fallbacks. Keep dependency additions minimal and document them. Do not add a second chart library or a marketing landing page.

Build the responsive shell with seven navigation destinations, role-aware visible actions, context header, compact corridor/horizon controls and evidence-drawer infrastructure. Use the real GET /session result. Display the server-derived data mode and source context when available. Routes without implemented capabilities show an honest not-yet-available or first-use state; do not display fake planning metrics or simulated live feeds.

Build reusable components: provenance/freshness badge, semantic status badge, typed error summary, empty state, task row, filter toolbar, controlled form fields with units, version selector, diff row, source citation, phase sequence, confirmation dialog and evidence panel. Use realistic long names and IDs in an isolated development-only preview gallery labelled UI FIXTURE. These fixtures must not enter release route data access.

Specify loading, empty, partial, permission-denied, stale, infeasible and service-unavailable states in the component gallery. Preserve keyboard focus on drawer/dialog transitions. Use restrained motion and prefers-reduced-motion. Lay out an empty planning canvas with correct hierarchy, not decorative chart data.

Capture actual browser screenshots at 1440x900 and 390px width. Inspect layout and correct clipping, text overflow, contrast, focus and inconsistent spacing. Run relevant component/browser checks and production build. Keep all navigation links valid; do not fake enabled action buttons.

Acceptance: a coherent custom visual language, usable responsive shell, functioning real login/session state, accessible components and visibly honest empty/unfinished states. Save the token and interaction decisions for Phase 11 and Phase 18; do not claim the planning product is complete.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-03.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.


---

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


---

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


---

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


---

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


---

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


---

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


---

# Phase 10 - Durable solve jobs and complete planning APIs

Copy-ready implementation prompt. Run after: 02, 08-09.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 28, 31, 33-34, 42-43.

Expose the real planning pipeline through durable asynchronous APIs and a separate worker.

Implement the agreed /api/v1 routes for snapshots, monthly/weekly solves, run status/cancellation, immutable plan versions, validation, candidate/unscheduled evidence and sources. A request validates scope, policy, snapshot and budget, commits a job/outbox/audit transaction and returns 202 with run ID and status URL. The request handler must not block on CPU solving. Fake successful handlers are unacceptable.

Use PostgreSQL FOR UPDATE SKIP LOCKED for short job-claim transactions. Solve outside transactions with a lease, heartbeat and fencing token. Publication checks current ownership/token and unique result keys; expired workers cannot publish twice or overwrite a newer result. Implement bounded retry and a visible failed-job state. At-least-once delivery requires idempotency; do not claim exactly-once execution.

Use Idempotency-Key for mutations and If-Match for mutable aggregate commands. Define request-fingerprint conflict behavior, stale ETags, validation errors, role denials, rate limits and dependency failure responses. A completed INFEASIBLE run is a domain outcome, not HTTP 500. Separate HTTP state, job state, solver result, checker verdict, applicability and approval eligibility in schemas.

Detect snapshot obsolescence while a run is in flight. Preserve historical artifacts but prevent silent activation of obsolete results. Return genuine status transitions; no simulated progress percentage or promised completion time. Implement modest scoped polling with cancellation/backoff in the frontend API layer; use generated types. Do not add WebSockets simply for appearances.

Acceptance integration tests with real PostgreSQL: duplicate submit; mismatched key/body; stale ETag; worker crash; lease expiry; stale worker publication; source update during solve; cancellation; unauthorized run access; API/database outage. Verify only a checked, correctly versioned result can be presented as usable. Show a browser-started real solve reaching a persisted outcome through this path.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-10.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.


---

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


---

# Phase 12 - Evidence-backed Why, Why-Not and bounded repair

Copy-ready implementation prompt. Run after: 07-11.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 24-25, 31-32.

Implement useful explanations from stored facts and controlled counterfactuals. Do not add an LLM to manufacture reasoning.

Create a typed reason catalogue distinguishing INPUT_BLOCKED, CANDIDATE_REJECTED, NO_CANDIDATE_IN_DOMAIN, MODEL_INFEASIBLE, FEASIBLE_BUT_UNSELECTED and SEARCH_INCOMPLETE. Every reason references its snapshot/run/candidate/rule versions and carries precise observed/required values, units, affected records and proof status. A timeout cannot become a definitive impossibility explanation.

For selected assignments show eligibility, readiness, compatibility evidence, resource/window conditions, priority and objective contribution. These facts explain admissibility; they do not automatically prove why this choice beat every alternative. Make comparative claims only after a real controlled counterfactual solve with the task/candidate forced and the same policy/domain. Identify the objective tier that changed, or report inconclusive.

Implement a bounded repair search: up to ten permitted single edits, then a documented small pair search if budget remains. Edits may move optional unlocked work, substitute a qualified available resource, select a validated alternate package/window or request a parent-week amendment. A longer access request remains AWAITING_AUTHORITY until authorized input actually changes. Never relax safety/protection, required isolation, unknown/prohibited compatibility, mandatory deadlines or operational commitments.

Trial repairs are non-publishable artifacts with requested edit, affected versions, required role, checker outcome, objective difference, remaining conflicts and runtime. Accepting a repair performs authorized input revisions with ETags and then a fresh normal solve. It does not directly mutate the last plan or reuse a hypothetical result as an approved version.

If using CP-SAT assumptions, verify support for each reified constraint form. A sufficient infeasible core is not necessarily minimal. Unsupported or incomplete diagnostics must remain explicit; no invented binding cause. Diagnostic relaxations are permanently non-publishable.

Connect the evidence drawer and repair review to real endpoints. Acceptance: precise unavailable-machine reason, UNKNOWN rule reason, time-budget uncertainty, forced alternative comparison, valid optional-work move, unauthorized longer-window request and no-permitted-repair escalation. Every displayed reason must resolve to stored evidence. Test that accepting a stale repair fails safely and never bypasses normal approval gates.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-12.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.


---

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


---

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


---

# Phase 15 - Human review, programme approval and audit integrity

Copy-ready implementation prompt. Run after: 02, 09-14.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 8-9, 31, 33-34.

Implement accountable human programme review and approval with atomic freshness checks.

Implement versioned lock/review/approval APIs and UI. Review actions bind exact immutable plan content, snapshot, checker result and parent lineage. Scope and delegated permission are checked server-side. Infrastructure administrator cannot approve by virtue of admin status. Rule author cannot self-approve a production rule where separation is required; TEST approval policy remains explicit.

In the approval transaction re-check the relevant current-version/freshness epoch, plan hash, VALID result, mandatory evidence, reconciliation, ETag and role. Prevent a concurrent relevant input mutation from slipping between validation and commit by using a documented transaction/locking or version-epoch strategy shared with the mutation path. A later event may mark applicability stale without rewriting the historical approval decision. Test the race, not merely sequential requests.

Locks identify task/assignment fields and authority category, not an ambiguous whole-plan Boolean. Authorized users can revise planner-controlled locks through an audited new revision. Operational reservations and completed history are not unlockable by this workflow. Show approval-block reasons and actionable navigation to the responsible evidence/input.

Persist append-only decisions and audit events containing actor/scope/time/reason, before/after references, correlation and content hash. Application-role permissions prohibit update/delete of history. If a hash chain is used, document concurrency and external anchoring limitations; it is tamper-evident within stated assumptions, not DBA-proof immutability. Generate an evidence export with provenance, status and source/version manifest. A proposal export is never an official Railway grant.

Acceptance: reviewer/approver permissions, stale version rejection, update/approval concurrency race, rejected invalid plan, missing-parent reconciliation, preserved historical decisions, duplicate command idempotency, audit linkage and server-enforced read-only metrics. Verify no grant, extension, signal-control or release endpoint exists. The UI must say programme proposal/approval accurately and keep external authority observations visually distinct.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-15.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.


---

# Phase 16 - Execution feedback, partial work and estimate review

Copy-ready implementation prompt. Run after: 04, 13, 15.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 9, 13, 35-36.

Complete the feedback loop using authoritative observations or explicitly fictional TEST observations.

Implement execution-record intake linking original task/demand, proposed assignment, external authority reference when available, actual start/restoration/release timestamps, quantity completed, units, resource use and deviation reason. Validate chronology, source version, scope and units. Preserve correction revisions and distinguish missing data from zero duration/output.

The external authority mirror consumes configured observations. It does not issue grants, extensions or releases. Reject unsupported transitions or route them to reconciliation according to the source contract. Planned finish time alone never advances it. In TEST mode, a user may create labelled test observations through the same normalized intake; that does not create real-world authority.

Partial completion creates a governed residual-work revision linked to the original demand and outcome, with owner confirmation of remaining quantity, site state, dependencies and applicable deadline/priority. Avoid duplicate demand and double-counted productive quantity. A recorded block release does not prove all maintenance tasks finished. A corrected completion observation invalidates affected current planning and metrics through the event pipeline.

Calculate plan-versus-actual quantity, duration and overrun only when comparable units and authoritative reference times exist. Explain missing attribution instead of inventing actual delay. Create an estimate-review workflow using deterministic summaries; estimate changes require a new reviewed version. Do not train ML in this phase or silently learn from fictional outcomes.

Add Data & Outcomes forms and outcome details linked back to plan/evidence/audit. Present unresolved chronology or duplicate-source conflicts in a reconciliation queue. Keep personal identifiers minimized and role-scoped.

Acceptance: full completion, partial work, missing release, corrected outcome, duplicate event, mismatched unit, invalid chronology, residual task not double-counted, still-occupied resource preserved, and a reviewed estimate used only by a later snapshot. Demonstrate the loop from original task to checked proposal to accepted fictional actuals to residual/next planning input.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-16.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.


---

# Phase 17 - Failure recovery, security and scaling evidence

Copy-ready implementation prompt. Run after: 00-16.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 33-34, 41-43, 51, 55-58.

Harden and benchmark the actual bounded application. This phase must produce evidence, not a 'production-ready' badge.

Run the requirement-linked regression suite, tiny exhaustive oracle, checker mutations, PostgreSQL/API integration and browser journeys. Add failure injection for worker termination, lease expiration, database/identity outage, stale run publication, retry storms, malformed imports, partial batch failure and approval concurrency. Invalid or unavailable data must never yield a silently current approved proposal.

Review OIDC/session/CSRF/CORS controls, role/territory isolation, RLS pool reuse, secrets, dependency/image vulnerabilities, import limits, export formula safety and log redaction. Use maintained security checks and record actual findings and fixes. Do not claim certification or zero vulnerabilities solely from a scanner. Security fixes need regression tests that demonstrate the previously possible failure.

Benchmark declared synthetic workloads at 10, 30 and 100 tasks with multiple seeds and varied window density, package choices and resource contention. Attempt 300 tasks only as an explicitly exploratory case after smaller workloads remain safe and within resource limits. Measure candidate generation, conflicts/model construction, CP-SAT stages, checker, API round trip, peak memory, status and domain truncation separately. Use repeated runs and report sample count, median and tail behavior. Name hardware/configuration; do not extrapolate to a whole division from task counts.

The blueprint's 30-task/30-second weekly and 60-task/60-second monthly budgets are engineering targets, not established facts. Keep resource caps and honest timeout behavior even if targets fail. Profile first; optimize the dominant cost with sparse indexing or a documented CP-SAT representation change. Re-run correctness oracle and checker tests after any model optimization. No test-set-specific canned shortcut.

Exercise backup and restore in a disposable environment; measure what was restored and how long it took. Verify a release can run offline with pre-pulled images, local auth, fonts and TEST data. Runtime must not secretly depend on analytics/CDN/external AI. Record any gap against proposed RPO/RTO instead of marking it passed without a drill.

Acceptance: reproducible benchmark report with raw results; classified unresolved issues; no known critical authorization or false-feasibility defect accepted for demonstration; failure paths visible and recoverable; an honest measured supported envelope. If a core gate fails, fix it or mark release blocked—never compensate with presentation polish.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-17.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.


---

# Phase 18 - Final visual craftsmanship and accessibility pass

Copy-ready implementation prompt. Run after: 11-17.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: DESIGN_BRIEF.md and 32.

Act as the final product designer and frontend engineer. Refine the implemented application, preserving all working contracts and planning behavior.

Use the Signal & Slate brief as art direction. Inspect the actual browser at 1280x800, 1440x900, 1920x1080, tablet and 390px mobile review. Capture the current screens first. Identify concrete defects in hierarchy, spacing, typography, density, chart readability, form feedback, status semantics and responsive behavior. Make purposeful corrections; do not replace the app with a new visual template.

Give special attention to the weekly workbench: queue/chart/drawer balance, clear chainage/time rulers, explicit track identity, restrained train lines, selected maintenance emphasis, resource conflicts and readable phase detail. A user must distinguish TEST data, provisional allocation, checked proposal, stale applicability and programme approval without memorizing colours. Preserve exact meaning of all status labels.

Polish navigation, empty states, import errors, unscheduled work, no solution, permission denial, server outage, retry behavior, confirmations and destructive-looking actions. Remove dead controls. Long source names and IDs must wrap or disclose without hiding important content. Avoid huge headings, decorative maps, unnecessary charts, dense tooltip-only evidence or excessive motion.

Verify keyboard-only operation, focus restoration, screen-reader labels, table alternatives, measured colour contrast, reduced motion and 200% zoom. A planning chart may have intentional internal horizontal navigation; the page itself should not spill off-screen. Mobile review must retain critical warnings and provenance even when chart editing uses a simpler form/list.

Use actual API/database TEST scenarios for screenshots: empty first use; populated maintenance; monthly view; weekly with evidence drawer; unknown rule; infeasible solve; edit during run; PlanDiff; blocked approval; quarantined import; outcome residual work. Do not generate mockup images to stand in for application evidence. Use interaction checks, not screenshots alone, to validate controls.

Acceptance: fix all observed blocking usability/accessibility issues; save before/after evidence with fixture/application versions; run relevant browser regressions and production build; confirm no hardcoded planning values were introduced during polishing. Report remaining visual limitations honestly. The final interface should feel like a coherent railway planning product whose beauty supports confident decisions.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-18.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.


---

# Phase 19 - Release rehearsal, judge challenge and handover

Copy-ready implementation prompt. Run after: 00-18 complete with evidence.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 40, 44-45, 52-59.

Produce a reproducible hackathon release from the working application. Do not add new major features during release hardening.

Audit every core acceptance item against actual code, passing tests and screenshots. Distinguish COMPLETE, PARTIAL, BLOCKED and NOT_RUN. Confirm 60-task monthly and up-to-30-task weekly scope actually supported by the fixture and benchmark, or report a smaller measured scope clearly. Confirm no runtime mocks, fake live badges, canned plan outputs, static KPI constants, unauthorized Railway data or external authority actions remain.

Build a clean-install and offline-demo runbook: prerequisites, pinned images/dependencies, configuration, migrations, local identity setup, explicit TEST seeding, service start, smoke checks, backup/restore and shutdown. Seeding must require an explicitly disposable TEST database; never automatically reset an existing dataset. Rehearse from a clean environment and record the exact versions/commands.

Prepare an executable challenge harness and a three-minute demonstration: source/snapshot context; monthly-to-weekly link; real solve/check; evidence for one selected and one rejected option; evaluator-chosen edit; genuine status transitions; fresh PlanDiff/metrics; human programme review. The evaluator must be able to choose a valid edit not mapped to a canned scenario response. Include a truthful unchanged outcome, no-benefit case and impossible mandatory scenario.

Create a release evidence bundle: acceptance matrix; test results; benchmark raw files; screenshots; API schema; fixture manifest/hash; rule/topology/policy versions; known limitations; dependency/licence inventory; operations runbook; architecture updates reflecting code. Update diagrams when actual implementation differs. Do not claim the blueprint itself proves runtime behavior.

Provide the demo script and recording instructions; record a video only if separately requested or explicitly part of the implementation task. Label time-compressed/precomputed footage, and retain a continuous evidence capture when recording. No fabricated latency, savings, safety or Railway approval claims.

Acceptance: a fresh user can follow the runbook; arbitrary valid edits use the same engine; all publishable plans pass the independent checker; metrics reproduce; locks and stale states behave correctly; offline rehearsal succeeds; outstanding dependencies are visible. Return the release location, actual supported scope, reproduction steps, measured results and remaining Railway pilot gates. Do not push/publish/deploy externally without task authorization.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-19.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.


---

# Optional Phase 20 - Authorized Railway shadow pilot

Use MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md and the existing implementation state. This phase is PILOT LATER, not part of the initial hackathon build. Execute only after the user requests pilot work and the required owner approvals and input contracts exist.

Prerequisites: core release gates pass; Railway sponsor and responsible domain/data/security owners are named; permitted datasets/interfaces, retention, access scopes and local rule applicability are documented. If these are absent, produce a precise readiness/dependency report and interface specification. Do not invent payloads, claim a live connection or use fictional records as authorized Railway data.

Implement only the approved read-only export/API adapter using the established common contract. Preserve source identifiers, versions, issue/valid timestamps, coverage manifests, error semantics and reconciliation rules. Credentials remain in approved secret storage and never enter frontend bundles, logs, public commits or prompts. Test auth failure, missing pages, partial exports, late/out-of-order events, schema drift, source outage and replay. A connector's HTTP success is not sufficient to label its data complete or fresh.

Validate actual selected-corridor topology, route/electrical footprints, compatibility, resource skills/travel, readiness, deadlines and authority observation mappings with the named owners. Record gaps as unknown and block affected publishability. Maintain TEST and Railway partitions, with no badge-only promotion.

Run retrospective and prospective shadow comparisons against the existing process on a bounded weekly scope, using monthly context. Prevent hindsight leakage in replay. Capture officer corrections, rejected recommendations, review effort, constraint violations, baseline comparisons and actual outcomes. No external operational system is controlled; proposal export remains disabled unless separately approved and contract-tested.

Implement owner-approved retention, access review, backup/restore, incident handling and audit export. Train users on infeasible, stale-data, lock-conflict and rollback cases. If recommendations are unsafe or not useful, stop their use and return to the established process while investigating.

Acceptance: signed or otherwise documented data/rule/role mapping; no unresolved critical access or false-feasibility defect; reproducible owner-agreed metrics; tested rollback; explicit go/no-go decision. Do not label the pilot successful simply because the connector works. End with actual evidence and unresolved adoption gates, without claiming Railway certification.


---

# Optional Phase 21 - Historical-data ML feasibility and controlled model evaluation

Use MASTER_PROMPT.md and the actual pilot/data state. FUTURE ONLY. Run only when the user requests this work and representative authorized historical data, usable labels and accountable ownership exist. The absence of data is a valid reason to stop at a data-readiness report; do not train a production-looking model on invented labels.

Choose one justified first use case: task-duration quantile estimation. Verify source joins, units, task definitions, quantity known at planning time, asset/site/resource context, interventions, missing outcomes and corrections. Identify which fields existed at the planning cutoff. Exclude actual completion/output facts that would leak the future. Assess consent/access/retention constraints and subgroup coverage; do not invent a universal adequate sample size.

Create temporal training/validation/test separation and, where data allows, a location holdout. Preserve a frozen untouched test set. Compare against a transparent median-by-task-type baseline and the existing reviewed estimate policy. Evaluate quantile loss, interval coverage, underestimation, subgroup errors and downstream planning outcomes on fixed replay snapshots. Do not substitute classification accuracy for duration quality.

Only after this audit, select a modest supported model justified by data and benchmark it. No automatic XGBoost/SHAP checkbox. Explain feature limitations; feature attribution is not causal proof. Keep constraints, mandatory priority and authority decisions deterministic and owner-controlled. The model supplies estimates/scenarios, never permission or a grant.

Version datasets/features/models, document training and licensing, monitor missingness/temporal/geographic drift and retain the deterministic fallback. Integration remains shadow-only until reviewed. Compare whether predicted estimates actually improve planning decisions without degrading required coverage or violating constraints. A predictive metric gain alone is not adoption evidence.

Acceptance: reproducible authorized dataset manifest, leakage review, baseline comparison, honest holdout results and uncertainty, rollback behavior and named owner approval before operational use. If no meaningful improvement appears, retain the deterministic system and report that outcome. Update claims only to match actual measured evidence.


---

# Resume prompt

Continue SAMARATH from the last verified checkpoint in this repository.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md, applicable repository instructions and docs/IMPLEMENTATION_STATE.md. Inspect the actual working tree, previous phase report and failing/incomplete checks. Do not infer completion from a previous assistant's prose.

Resume the currently requested phase only. Preserve completed behavior and unrelated changes. Identify the first unmet acceptance criterion, reproduce it where possible, implement the smallest sound change and run relevant checks. Do not restart the project, replace the design system, regenerate all scaffolding or re-seed a populated database to avoid debugging.

If the prior action was blocked or NOT_RUN, verify whether the blocker is now resolved before claiming progress. Do not work around denied authorization. If the current phase is fully complete, report its evidence and the next eligible phase rather than silently executing optional pilot/ML work.

Update implementation state and the phase report with exact files, checks, evidence and remaining limits. Return a concise status grounded in actual execution.


---

# Focused failure / regression repair prompt

Diagnose and fix the concrete SAMARATH failure described in my message or captured in the current failing test/output. Read MASTER_PROMPT.md, implementation state, relevant contracts and recent changes first.

Reproduce the failure using the smallest faithful case. Classify whether it is a data-contract, authorization, domain, candidate, optimizer, independent-checker, worker/concurrency, API, frontend or environment issue. Trace the actual path before modifying code. Preserve evidence about the failing snapshot/run/version and redact secrets.

Fix the root cause with a regression test that would fail before the fix. Never disable the independent checker, drop a hard constraint, turn UNKNOWN into ALLOWED, accept stale approval, replace the actual service with a mock, or hardcode the expected schedule merely to pass. If the test expectation is wrong, justify it against the documented policy and an independent example before changing it.

For UI defects, inspect the actual browser state at the affected viewport and interaction, then verify the corrected screen and keyboard behavior. For scheduling defects, use the tiny oracle or hand-calculated case and independent validation. For races, force the problematic interleaving rather than testing only a sequential happy path.

Run targeted regression and relevant integration checks, compare the previous and new behavior, and update the phase report/state. Clearly mark anything not executed. Do not perform an unrelated rewrite or claim the whole project is validated by this fix.
