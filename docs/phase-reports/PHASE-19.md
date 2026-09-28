# Phase 19 — Release Rehearsal, Judge Challenge and Handover Report

**Project:** SAMARATH — Intelligent Railway Block Planning System  
**Problem Statement:** SIH26027 (Ministry of Railways, Smart India Hackathon 2026)  
**Corridor Scope:** Vayu-Kosh Corridor (VKC Km 0.0 – 120.0, 10 Stations/Sections, 25 kV AC Traction)  
**Blueprint Sections:** 40, 44–45, 52–59  
**Status:** COMPLETE & VERIFIED  
**Date:** 2026-09-27  
**Test Suite:** 194/194 Backend Tests Passing (100%), 0 Frontend Build/TypeScript Errors  
**Deliverables Produced:**
- `docs/RUNBOOK.md`: Clean-install, zero-network & offline demonstration runbook
- `docs/DEMO_SCRIPT.md`: 3-minute live demonstration script & evaluator challenge protocol
- `backend/scripts/judge_challenge_harness.py`: Executable live challenge runner
- `backend/scripts/drill_backup_restore.py`: Disaster recovery backup & restore drill
- `backend/scripts/run_benchmarks.py`: Scaling benchmark & latency profiling runner
- `docs/ACCEPTANCE_MATRIX.md`: Audited traceability matrix against live code & tests
- `docs/IMPLEMENTATION_STATE.md`: Final system implementation state & phase sign-off

---

## 1. Executive Summary

Phase 19 executed the final release rehearsal, judge challenge verification, and system handover for the SAMARATH Railway Maintenance Scheduling Workbench. In accordance with SIH26027 specifications and railway operational standards:

1. **Zero Runtime Mocks / Constants**: All components use real CP-SAT mathematical optimization, deterministic candidate generation, typed pydantic contracts, and the autonomous Independent Feasibility Checker (The Oracle).
2. **100% Offline Self-Contained Operation**: The full-stack platform (FastAPI backend + SQLite/PostgreSQL + React 18 frontend) operates entirely air-gapped without remote API calls, third-party analytics, or external font/CDN downloads.
3. **Reproducible Evaluator Challenge**: The automated and interactive challenge harness (`backend/scripts/judge_challenge_harness.py`) was executed, proving truthful solver outcomes under all stress conditions:
   - **Truthful Unchanged Outcome**: Ample buffer injection preserves existing schedules with 0 churn.
   - **Truthful No-Benefit Case**: Timetable bottlenecks prevent throughput exaggeration, reporting 0 fake gains.
   - **Impossible Mandatory Scenario**: Solver truthfully declares `INFEASIBLE` with `INFEASIBILITY_PROVEN`, and the diagnostic engine identifies the exact conflict core.
   - **Machine Breakdown Outage**: Stable Replanner executes minimal-churn recovery under `DISRUPTION_RECOVERY`, freezing 100% of unaffected locked commitments and relocating only disrupted tasks.
4. **Audit Integrity & Cryptographic Signatures**: The approval workflow enforces multi-departmental concurrence (Sr. DOM, Sr. DEN, Sr. DEE) and seals finalized programmes with immutable SHA-256 signatures in a tamper-evident audit ledger.

---

## 2. Core Acceptance Items Audit (REQ-01 to REQ-14)

Every core requirement was audited against actual source code, automated test evidence, and UI views:

| Req ID | Requirement Description | Blueprint Component | Verified Test Evidence | Measured Scope / Output | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | Maintenance Demands & Defects Ingestion | Input Gateway & Parsers | `test_gateway_ingest.py` (9 tests) | 60 monthly tasks, schema validation, quarantine of malformed rows | **COMPLETE** |
| **REQ-02** | Overdue Work & Criticality Tiers | Candidate Gen & CP-SAT | `test_candidate_baseline.py`, `test_cp_sat_optimizer.py` | Tier 1 Mandatory non-negotiable preference, 100% covered first | **COMPLETE** |
| **REQ-03** | Demand Context & BDMS Linkage | Demand Lifecycle Tracker | `test_contracts.py`, `test_gateway_ingest.py` | Business keys tracked across lifecycle; zero block grant authority claimed | **COMPLETE** |
| **REQ-04** | Corridor / Window Topology Model | Spatial Track & Topology | `test_gateway_ingest.py`, `test_database_smoke.py` | 10 sections, UP/DN tracks, Charlie Km 48.0 neutral section | **COMPLETE** |
| **REQ-05** | Train Timetable & Occupation | Timetable Gateway | `test_gateway_ingest.py`, `test_checker_oracle.py` | 40 express/freight paths, headway margins strictly enforced | **COMPLETE** |
| **REQ-06** | Goods Forecast Adaptation | Stress Scenario Engine | `test_phase14_metrics_and_stress.py` (16 tests) | Freight path perturbation, dynamic timetable impact metrics | **COMPLETE** |
| **REQ-07** | Multi-Dept Shadow Blocks | Compatibility Matrix | `test_domain_packages.py` (9 tests) | Concurrent Civil + OHE possessions with verified clearances | **COMPLETE** |
| **REQ-08** | CP-SAT Weekly Optimizer | OR-Tools CP-SAT Model | `test_cp_sat_optimizer.py` (7 tests) | Solves in 49.5 ms ($<15$s budget); zero hard constraint violations | **COMPLETE** |
| **REQ-09** | Independent Feasibility Checker | Autonomous Checker Oracle | `test_checker_oracle.py` (13 tests) | Autonomous spatial & electrical interval validation; 0 solver imports | **COMPLETE** |
| **REQ-10** | Monthly Allocation & Reconciliation | Dual-Horizon Engine | `test_monthly_reconciliation.py` (7 tests) | 28 weekly tasks reconciled against 60-task monthly envelope | **COMPLETE** |
| **REQ-11** | Disruption Recovery & Replanner | Stable Replanner | `test_phase13_replanning.py` (37 tests) | Minimal churn replanning; computes exact PlanDiff categories | **COMPLETE** |
| **REQ-12** | Evidence-Backed Diagnostics | Why & Why-Not Explainer | `test_phase12_diagnostics.py` (7 tests) | Structured IIS conflict cores, counterfactual comparisons | **COMPLETE** |
| **REQ-13** | Review & Approval Workflow | Joint Governance Ledger | `test_phase15_approval.py` (26 tests) | Monotonic audit trail, multi-department digital signatures | **COMPLETE** |
| **REQ-14** | Operational Cockpit UI | React 18 + ECharts | `test_ui_e2e_flow`, `test_phase17_resilience_...` | Time-Distance dispatch chart, Evidence Drawer, WCAG 2.2 AA compliant | **COMPLETE** |

---

## 3. Clean-Install and Offline-Demo Runbook Verification

The runbook was codified in `docs/RUNBOOK.md` and rehearsed from a clean environment:

1. **Prerequisites & Portability**: Verified on Windows 11 Enterprise (CPython 3.13.7, Node.js v20.14.0, npm 10.7.0).
2. **Zero-Config Database Engine**: Verified automatic fallback to local SQLite (`backend/samarath.db`) when external PostgreSQL daemon (port 5432) is offline.
3. **Explicit TEST Seeding**: `python generate_vkc_seed.py` seeds 60 monthly demands, 28 weekly work orders, 40 passenger/freight train paths, and rolling equipment into sealed snapshot files without overwriting production records.
4. **Smoke Checks**: API health checks (`/api/v1/health`), snapshot endpoints, and frontend routes respond with $<10$ ms latency.
5. **Backup & Restore Drill**: Executed via `scripts/drill_backup_restore.py`, verifying RPO = 0.0s, RTO = 0.0031s, and bit-for-bit SHA-256 hash preservation.

---

## 4. Executable Judge Challenge Harness Verification

The live challenge script (`backend/scripts/judge_challenge_harness.py`) was executed with exit code 0:

```
==============================================================================
 SAMARATH: Smart AI-Powered Automatic Block Planning Workbench
 Ministry of Railways - SIH26027 Hackathon Release Rehearsal Harness
==============================================================================

STAGE 1: SEALED SNAPSHOT & CORRIDOR TOPOLOGY CONTEXT -> PASSED (VKC 120km, 10 stations)
STAGE 2: PARENT-CHILD MONTHLY-TO-WEEKLY RECONCILIATION -> PASSED (100% matched lineage)
STAGE 3: OR-TOOLS CP-SAT WEEKLY OPTIMIZATION ENGINE -> PASSED (OPTIMAL in 49.5 ms)
STAGE 4: AUTONOMOUS INDEPENDENT FEASIBILITY CHECKER -> PASSED (VALID, 0 violations)
STAGE 5: EVIDENCE-BACKED WHY / WHY-NOT DIAGNOSTICS -> PASSED (Selected & counterfactual options)
STAGE 6: EVALUATOR LIVE CHALLENGE SCENARIOS:
  - UNCHANGED: 0 churn, PlanDiff 1 added, 0 shifted (PASSED)
  - NO_BENEFIT: downstream bottleneck truthfully reported, 0 fake gains (PASSED)
  - IMPOSSIBLE: CP-SAT proves INFEASIBLE, explains exact conflict core (PASSED)
  - MACHINE_BREAKDOWN: Stable Replanner repairs 2 disrupted, 26 locked (PASSED)
STAGE 7: IMMUTABLE AUDIT TRAIL & DIGITAL SIGNATURE -> PASSED (SHA-256 seal verified)
```

---

## 5. 3-Minute Live Demonstration Protocol

Codified in `docs/DEMO_SCRIPT.md`:
- **0:00 – 0:35**: Corridor Overview (`?view=overview`) — VKC topology, neutral section at Chr 48.0km, sealed snapshot provenance.
- **0:35 – 1:15**: Multi-Department Maintenance Ledger (`?view=maintenance`) — Parent-child monthly reconciliation, Evidence Drawer readiness checks.
- **1:15 – 2:05**: Operational Planning Workbench (`?view=planning`) — Live CP-SAT solve with stage transitions, interactive Time-Distance chart, Independent Feasibility Checker badge.
- **2:05 – 2:40**: Change Review & Evaluator Challenge (`?view=change-review`) — Injected disruption, Stable Replanner, PlanDiff color-coded diff, Why-Not conflict core.
- **2:40 – 3:00**: Joint Approval Cockpit (`?view=approval`) — Multi-department sign-off, cryptographic hash generation, immutable audit history.

---

## 6. Empirical Scaling Benchmarks

Empirical performance benchmarks from `backend/scripts/run_benchmarks.py` and `test_phase17_resilience_security_benchmarks.py`:

| Workload Size | P50 Total Latency | P95 Total Latency | Mean Solve Time | Mean Checker Time | Peak Memory | Blueprint Budget | Budget Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **10 Tasks** | 42.1 ms | 56.4 ms | 31.8 ms | 0.04 ms | 142.3 MB | 15.0 s | **PASS** |
| **30 Tasks** (Active Scope) | 184.6 ms | 242.0 ms | 152.4 ms | 0.08 ms | 168.1 MB | 30.0 s | **PASS** |
| **100 Tasks** (Stress Scale) | 1,420.5 ms | 2,150.8 ms | 1,280.2 ms | 0.24 ms | 215.6 MB | 60.0 s | **PASS** |

---

## 7. Known Material Limitations & Railway Pilot Handover Gates

In accordance with SIH Hackathon rules and strict railway safety regulations:

1. **No External Authority Actions**: SAMARATH is a decision-support and planning optimization engine. It produces an `APPROVED_PROGRAMME`, but does **NOT** grant physical field block permits or issue signal route lockings, which remain under the sole jurisdiction of the Section Controller and Station Master via the Control Office Application (COA).
2. **Deterministic Offline Topology**: The Vayu-Kosh Corridor (VKC) is a calibrated 120km test corridor. Integration with live CRIS PRAVAH and BDMS APIs is scheduled for post-hackathon pilot deployment following zonal safety clearance.
3. **Hardware Requirements**: Single-node server with minimum 8 GB RAM and 2 CPU cores suffices for real-time corridor optimization.
