# Acceptance Matrix and Requirements Traceability - SAMARATH

**Project:** SAMARATH  
**Problem Statement:** SIH26027 (Ministry of Railways, Smart India Hackathon 2026)  
**Status:** BASELINE CONTROL DOCUMENT (Phase 00)  
**Last Updated:** 2026-09-26  

---

## 1. Traceability Legend

- **Status Values:**
  - `EXISTING_AND_TESTED`: Working implementation backed by automated passing tests.
  - `EXISTING_UNVERIFIED`: Code exists in preliminary form but lacks automated test evidence or PostgreSQL integration.
  - `MISSING`: Capability not yet implemented.
  - `DEFERRED`: Planned for post-hackathon pilot stages (e.g., live CRIS PRAVAH API connectors, operational ML models).

> [!IMPORTANT]
> **Audit Honesty Invariant:** No capability is marked `EXISTING_AND_TESTED` merely because its design is documented. Status reflects verified executable software.

---

## 2. SIH26027 Requirements Traceability Matrix

| Req ID | SIH Problem Statement Requirement | Blueprint Component | Input / Output Schema | Acceptance Verification Test | Status |
|---|---|---|---|---|---|
| **REQ-01** | **Maintenance Demands & Defects Ingestion** | Input Gateway / Task Ingestion | **In:** Departmental JSON/CSV<br>**Out:** Normalized `Task` entities | Ingest valid & malformed records; verify schema validation and quarantine of bad rows (`test_gateway_ingest.py`). | **EXISTING_AND_TESTED** |
| **REQ-02** | **Overdue Work & Criticality Tiers** | Priority Policy & Ranking Engine | **In:** `Task.deadline_utc`, `Task.criticality`<br>**Out:** Ranked candidates & priority weights | Modifying task due date elevates priority; statutory safety tier receives non-negotiable preference (`test_candidate_baseline.py`, `test_cp_sat_optimizer.py`). | **EXISTING_AND_TESTED** |
| **REQ-03** | **Demand Context & BDMS Linkage** | Demand Lifecycle Tracker | **In:** Demand business keys<br>**Out:** Traceable status without grant authority | Demands display lifecycle without claiming field block grant authority (`test_contracts.py`, `test_gateway_ingest.py`). | **EXISTING_AND_TESTED** |
| **REQ-04** | **Corridor / Window Availability Model** | Spatial Track Topology & Window Model | **In:** Corridor topology, maintenance windows<br>**Out:** Feasible spatio-temporal placement slots | Ingest VKC topology, stations, UP/DN segments, neutral section (`test_gateway_ingest.py`, `test_database_smoke.py`). | **EXISTING_AND_TESTED** |
| **REQ-05** | **Train Timetable & Occupation Integration** | Train Timetable Gateway | **In:** Working Timetable (WTT) train paths<br>**Out:** Track occupation intervals & safety margins | Ingest VKC train paths across weekly cycle (`test_gateway_ingest.py`, `test_checker_oracle.py`). | **EXISTING_AND_TESTED** |
| **REQ-06** | **Goods Forecast from Control Office** | Forecast Scenario Engine | **In:** Freight path forecasts with issue vintages<br>**Out:** Scenario-specific constraint envelopes | Inject freight forecast vintage; recompute plan and compare impact metrics (`test_phase14_metrics_and_stress.py`). | **EXISTING_AND_TESTED** |
| **REQ-07** | **Multi-Department Coordination (Shadow Blocks)** | Bundling Engine & Compatibility Matrix | **In:** Civil, OHE, S&T tasks on same corridor<br>**Out:** Unified multi-department block package | Formulate single traffic possession containing concurrent civil + OHE work with verified safety clearances (`test_domain_packages.py`). | **EXISTING_AND_TESTED** |
| **REQ-08** | **Intelligent Prioritization & Optimization** | OR-Tools CP-SAT Weekly Optimizer | **In:** `Snapshot`<br>**Out:** `MaterializedAssignment`, `SolverRun` | Solve weekly workload with `PROGRAMME_IMPROVEMENT` profile; verify zero hard constraint violations (`test_cp_sat_optimizer.py`). | **EXISTING_AND_TESTED** |
| **REQ-09** | **Independent Feasibility Checker (Oracle)** | Independent Deterministic Checker | **In:** Raw `Snapshot` + candidate assignments<br>**Out:** `ValidationResult` (PASS / FAIL / UNKNOWN) | Inject deliberate track collision; Independent Checker must reject plan even if solver erroneously marks it feasible (`test_checker_oracle.py`). | **EXISTING_AND_TESTED** |
| **REQ-10** | **Monthly Allocation & Weekly Reconciliation** | Dual-Horizon Planning Engine | **In:** 30-day demand bundle<br>**Out:** Monthly quota allocation & weekly reconciled schedule | Reconcile 7-day slice against monthly plan; flag unallocated or displaced tasks (`test_monthly_reconciliation.py`). | **EXISTING_AND_TESTED** |
| **REQ-11** | **Disruption Recovery & Stable Replanning** | Event-Driven Replanner (`DISRUPTION_RECOVERY`) | **In:** Incumbent plan + disruption event<br>**Out:** New plan with minimal churn & `PlanDiff` | Inject machine outage; solver repairs affected blocks while preserving all unaffected locked commitments (`test_phase13_replanning.py`). | **EXISTING_AND_TESTED** |
| **REQ-12** | **Evidence-Backed Why and Why-Not Diagnostics** | Explainability Engine & Counterfactual Core | **In:** Unscheduled task ID + solver run<br>**Out:** Structured `Reason` with conflict core | Query why a mandatory task was rejected; receive exact conflicting train/machine IDs and policy-permitted repair options (`test_phase12_diagnostics.py`). | **EXISTING_AND_TESTED** |
| **REQ-13** | **Human Review & Approval Workflow** | Programme Review & Audit Ledger | **In:** Validated plan + reviewer edits<br>**Out:** `APPROVED_PROGRAMME` with cryptographic hash | Joint review workflow records reviewer approval; tampered plan fails hash validation (`test_phase15_approval.py`). | **EXISTING_AND_TESTED** |
| **REQ-14** | **Operational Cockpit UI (Signal & Slate)** | React 18 + TS Workbench | **In:** REST APIs<br>**Out:** Interactive Time-Distance chart & Evidence Drawer | User inspects corridor timetable, drags or reviews blocks, inspects evidence drawer, and reviews PlanDiff across 7 destinations (`test_ui_e2e_flow`). | **EXISTING_AND_TESTED** |

---

## 3. Detailed Phase Exit Gates

| Phase | Phase Title | Exit Gate Criteria | Prerequisite | Status |
|---|---|---|---|---|
| **00** | **Repository Audit & Implementation Contract** | Pinned dependencies, frozen scope, source-of-truth API contracts, ADRs, and acceptance matrix documented. | None | **EXISTING_AND_TESTED** |
| **01** | **Runnable Foundation, DB & Typed Contracts** | Docker Compose PostgreSQL running, Alembic migrations apply full FK spine, Pydantic schemas validate with zero errors. | Phase 00 | **EXISTING_AND_TESTED** |
| **02** | **Real Login, Scoped Permissions & Sessions** | Role-based authentication (Planner, Operating Reviewer, Approver, Admin) with territory scoping. | Phase 01 | **EXISTING_AND_TESTED** |
| **03** | **Distinctive Design System & App Shell** | Signal & Slate theme implemented in React+TS; 7 destinations navigable with responsive layout. | Phase 01 | **EXISTING_AND_TESTED** |
| **04** | **Input Gateway & Fictional Corridor Seed** | CSV/JSON parsers for demands, trains, and resources with VKC demonstration seed dataset. | Phase 01 | **EXISTING_AND_TESTED** |
| **05** | **Readiness, Compatibility & Work Packages** | Departmental compatibility matrix and machine/crew readiness verification engine. | Phase 04 | **EXISTING_AND_TESTED** |
| **06** | **Sparse Candidate Generation & Greedy Baseline** | Time-indexed candidate generator and deterministic greedy baseline benchmark. | Phase 04, 05 | **EXISTING_AND_TESTED** |
| **07** | **Independent Feasibility Checker (Oracle)** | Deterministic checker evaluating track, OHE, and resource safety independent of solver. | Phase 04, 05 | **EXISTING_AND_TESTED** |
| **08** | **Real CP-SAT Weekly Optimizer** | Mathematical optimization model implementing `PROGRAMME_IMPROVEMENT` and `DISRUPTION_RECOVERY`. | Phase 06, 07 | **EXISTING_AND_TESTED** |
| **09** | **Monthly Allocation & Weekly Reconciliation** | Parent-child reconciliation between 30-day allocations and 7-day operational schedules. | Phase 08 | **EXISTING_AND_TESTED** |
| **10** | **Durable Solve Jobs & Complete APIs** | PostgreSQL leased worker queue executing asynchronous solve jobs with status endpoints. | Phase 08, 09 | **EXISTING_AND_TESTED** |
| **11** | **Operational Planning Workbench UI** | Interactive Time-Distance string chart with ECharts, possession bands, and selection sync. | Phase 03, 10 | **EXISTING_AND_TESTED** |
| **12** | **Evidence-Backed Why/Why-Not & Repair** | Structured explanation of unscheduled tasks and verified counterfactual repair suggestions. | Phase 08, 11 | **EXISTING_AND_TESTED** |
| **13** | **Event-Driven Stable Replanning & PlanDiff** | Minimal-churn replanning under injected disruptions with visual diff highlighting. | Phase 08, 12 | **EXISTING_AND_TESTED** |
| **14** | **Calculated Metrics & Stress Scenarios** | Transparent metric computation comparing baseline vs CP-SAT across stress scenarios. | Phase 08, 13 | **EXISTING_AND_TESTED** |
| **15** | **Human Review & Programme Approval** | Multi-department joint review, signature record, and immutable audit history. | Phase 02, 11 | **EXISTING_AND_TESTED** |
| **16** | **Execution Feedback & Estimate Review** | Ingestion of field progress, partial work tracking, and duration revision recommendations. | Phase 15 | **EXISTING_AND_TESTED** |
| **17** | **Failure Recovery & Performance Benchmarks** | Benchmark suites verifying candidate generation, solver latency, and worker crash recovery. | Phase 10, 14 | **EXISTING_AND_TESTED** |
| **18** | **Visual Craftsmanship & Accessibility Pass** | WCAG 2.2 AA compliance, contrast checks, keyboard navigation, and theme consistency. | Phase 11, 18 | **EXISTING_AND_TESTED** |
| **19** | **Release Rehearsal & Judge Challenge Package** | End-to-end rehearsal running live judge disruption challenge offline without internet. | All phases | **EXISTING_AND_TESTED** |
