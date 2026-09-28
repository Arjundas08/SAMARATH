# Typed API Contracts and Entity Specifications - SAMARATH

**Project:** SAMARATH  
**Problem Statement:** SIH26027 (Ministry of Railways, Smart India Hackathon 2026)  
**Status:** FROZEN SPECIFICATION (Phase 00)  
**Last Updated:** 2026-09-26  

---

## 1. Architectural Invariants and Wire Format

1. **Format:** Standard JSON over HTTPS REST.
2. **Timestamps:** ISO 8601 strings in UTC format (e.g., `2026-10-12T04:30:00Z`).
3. **Identifiers:** UUIDv4 for transactional and relational entities (`task_id`, `snapshot_id`, `plan_id`, `job_id`); human-readable formatted keys for business display (`TASK-TMS-0042`, `RUN-20261012-001`).
4. **Immutability:** `Snapshot`, `SolverRun`, `ValidationResult`, and `PlanVersion` are strictly immutable once created. Any edit produces a new revision.
5. **Errors:** RFC 7807 Problem Details representation for all HTTP 4xx/5xx responses.

---

## 2. Core Domain Entities (Source-of-Truth Contracts)

### 2.1 Task / MaintenanceDemand
Represents an individual work requirement submitted by an engineering department.

```json
{
  "task_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "business_key": "TASK-TMS-0012",
  "department": "ENGINEERING", // "ENGINEERING", "SIGNALLING", "ELECTRICAL"
  "sub_department": "TRACK_PWAY",
  "work_type": "BALLAST_CLEANING",
  "description": "Deep screening of plain track between Alpha and Bravo UP line",
  "station_from": "ALP",
  "station_to": "BRV",
  "track_segment_id": "SEC-01-UP",
  "chainage_start_km": 5.200,
  "chainage_end_km": 8.400,
  "duration_minutes": 240,
  "setup_buffer_minutes": 30,
  "restoration_buffer_minutes": 30,
  "total_block_minutes": 300,
  "criticality": "TIER_1_MANDATORY", // "TIER_1_MANDATORY", "TIER_2_SPEED_RESTRICTION", "TIER_3_CYCLIC"
  "deadline_utc": "2026-10-18T23:59:59Z",
  "preferred_windows": [
    {
      "window_start_utc": "2026-10-14T01:00:00Z",
      "window_end_utc": "2026-10-14T07:00:00Z"
    }
  ],
  "required_resources": [
    {
      "resource_type": "MACHINE",
      "resource_id": "BCM-02",
      "quantity": 1
    },
    {
      "resource_type": "CREW",
      "resource_id": "CREW-PWAY-A",
      "quantity": 1
    }
  ],
  "requires_power_block": true,
  "power_block_elementary_section": "ES-ALP-BRV-01",
  "requires_speed_restriction_after": true,
  "imposed_speed_kmh": 45,
  "demand_status": "VALIDATED", // "DRAFT", "SUBMITTED", "VALIDATED", "WITHDRAWN"
  "provenance_mode": "TEST", // "TEST", "SYNTHETIC_SCENARIO", "AUTHORIZED_IMPORT"
  "created_at_utc": "2026-10-01T10:00:00Z",
  "created_by": "pl_sharma_pway"
}
```

*Server-Derived Fields:* `total_block_minutes` ($duration + setup + restoration$), `demand_status`, `created_at_utc`.

---

### 2.2 Snapshot
An immutable point-in-time container encapsulating all inputs required for an optimization or verification run.

```json
{
  "snapshot_id": "c3d5f8a1-2b4e-4f7c-9a1d-8e6b3c2a1f0e",
  "snapshot_hash": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069",
  "corridor_code": "VKC",
  "horizon_start_utc": "2026-10-12T00:00:00Z",
  "horizon_end_utc": "2026-10-18T23:59:59Z",
  "provenance_mode": "TEST",
  "tasks_count": 28,
  "train_occupations_count": 280,
  "resource_calendars_count": 14,
  "locked_commitments_count": 3,
  "created_at_utc": "2026-10-11T18:00:00Z",
  "created_by": "solver_daemon",
  "is_sealed": true
}
```

*Server-Derived Fields:* `snapshot_hash` (deterministic cryptographic digest of all included records), `tasks_count`, `train_occupations_count`, `created_at_utc`, `is_sealed`.

---

### 2.3 CandidateManifest
A collection of candidate spatio-temporal placements for maintenance tasks generated before solver search.

```json
{
  "manifest_id": "e4f5a6b7-8c9d-0e1f-2a3b-4c5d6e7f8a9b",
  "snapshot_id": "c3d5f8a1-2b4e-4f7c-9a1d-8e6b3c2a1f0e",
  "total_candidates": 412,
  "candidates": [
    {
      "candidate_id": "cand-0012-01",
      "task_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "track_segment_id": "SEC-01-UP",
      "start_minute": 150, // Minutes from horizon epoch
      "end_minute": 450,
      "start_utc": "2026-10-12T02:30:00Z",
      "end_utc": "2026-10-12T07:30:00Z",
      "shadow_with_task_id": null,
      "train_conflict_penalty": 12.5,
      "is_valid_prefilter": true
    }
  ],
  "generation_duration_ms": 340
}
```

---

### 2.4 MaterializedAssignment
An individual task scheduled onto a specific track and time interval within a proposed plan.

```json
{
  "assignment_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "plan_id": "f7e6d5c4-b3a2-1f0e-9d8c-7b6a5f4e3d2c",
  "task_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "business_key": "TASK-TMS-0012",
  "track_segment_id": "SEC-01-UP",
  "start_utc": "2026-10-12T02:30:00Z",
  "end_utc": "2026-10-12T07:30:00Z",
  "duration_minutes": 300,
  "work_phase_schedule": {
    "setup_start_utc": "2026-10-12T02:30:00Z",
    "setup_end_utc": "2026-10-12T03:00:00Z",
    "work_start_utc": "2026-10-12T03:00:00Z",
    "work_end_utc": "2026-10-12T07:00:00Z",
    "restoration_start_utc": "2026-10-12T07:00:00Z",
    "restoration_end_utc": "2026-10-12T07:30:00Z"
  },
  "assigned_resources": [
    {
      "resource_type": "MACHINE",
      "resource_id": "BCM-02"
    },
    {
      "resource_type": "CREW",
      "resource_id": "CREW-PWAY-A"
    }
  ],
  "power_block_required": true,
  "power_block_section": "ES-ALP-BRV-01",
  "is_locked": false,
  "is_shadow_block": false,
  "bundled_with_task_ids": []
}
```

---

### 2.5 SolverRun
A record of an execution of the CP-SAT solver.

```json
{
  "run_id": "d1c2b3a4-5e6f-7a8b-9c0d-1e2f3a4b5c6d",
  "snapshot_id": "c3d5f8a1-2b4e-4f7c-9a1d-8e6b3c2a1f0e",
  "objective_profile": "PROGRAMME_IMPROVEMENT", // "PROGRAMME_IMPROVEMENT", "DISRUPTION_RECOVERY"
  "solver_engine": "ORTOOLS_CP_SAT",
  "solver_version": "9.10.4067",
  "solver_status": "OPTIMAL", // "OPTIMAL", "FEASIBLE", "INFEASIBLE", "TIME_LIMIT", "NOT_SOLVED"
  "objective_value": 4128.5,
  "solve_wall_time_seconds": 4.82,
  "num_variables": 1240,
  "num_constraints": 3480,
  "scheduled_tasks_count": 26,
  "unscheduled_tasks_count": 2,
  "created_at_utc": "2026-10-11T18:05:00Z"
}
```

---

### 2.6 ValidationResult (Independent Checker Oracle)
The authoritative certificate of correctness issued by the Independent Checker.

```json
{
  "validation_id": "val-98765432-10fe-dcba-9876-543210fedcba",
  "snapshot_id": "c3d5f8a1-2b4e-4f7c-9a1d-8e6b3c2a1f0e",
  "plan_id": "f7e6d5c4-b3a2-1f0e-9d8c-7b6a5f4e3d2c",
  "overall_verdict": "VERIFIED_FEASIBLE", // "VERIFIED_FEASIBLE", "VERIFICATION_FAILED", "UNKNOWN_BLOCKED"
  "checked_at_utc": "2026-10-11T18:05:08Z",
  "checks_passed": 18,
  "checks_failed": 0,
  "rule_evaluations": [
    {
      "rule_id": "RULE-SAFETY-01-TRACK-CONFLICT",
      "verdict": "PASS",
      "violation_count": 0,
      "details": "Zero overlapping train-block or block-block spatio-temporal collisions detected."
    },
    {
      "rule_id": "RULE-SAFETY-02-POWER-BLOCK-ISOLATION",
      "verdict": "PASS",
      "violation_count": 0,
      "details": "Mandatory OHE isolation elementary sections verified for 12 track machine tasks."
    },
    {
      "rule_id": "RULE-RESOURCE-01-CAPACITY",
      "verdict": "PASS",
      "violation_count": 0,
      "details": "All machine and crew assignments respect non-overlapping calendar capacity."
    }
  ],
  "violations": []
}
```

---

### 2.7 PlanVersion
A versioned, audit-ready operational block plan.

```json
{
  "plan_id": "f7e6d5c4-b3a2-1f0e-9d8c-7b6a5f4e3d2c",
  "plan_version_number": 3,
  "snapshot_id": "c3d5f8a1-2b4e-4f7c-9a1d-8e6b3c2a1f0e",
  "parent_plan_id": "e6d5c4b3-a2f1-0e9d-8c7b-6a5f4e3d2c1b",
  "validation_id": "val-98765432-10fe-dcba-9876-543210fedcba",
  "horizon_type": "WEEKLY", // "MONTHLY", "WEEKLY"
  "plan_status": "APPROVED_PROGRAMME", // "DRAFT_PROPOSAL", "CHECKED_FEASIBLE", "JOINT_REVIEW", "APPROVED_PROGRAMME", "STALE"
  "programme_authority_state": "RECOMMENDED", // "PROPOSED", "RECOMMENDED", "OPERATING_RATIFIED"
  "field_authority_state": "EXTERNAL_PERMIT_PENDING", // Read-only observation
  "metrics": {
    "total_tasks_demanded": 28,
    "total_tasks_scheduled": 26,
    "statutory_safety_compliance_pct": 100.0,
    "corridor_availability_hours": 142.5,
    "total_possession_hours": 58.0,
    "multi_dept_shadow_blocks_count": 8,
    "estimated_train_impact_index": 3.4
  },
  "approved_at_utc": "2026-10-11T19:30:00Z",
  "approved_by_officer": "sr_dom_operating_hq"
}
```

---

### 2.8 Reason (Structured Diagnostic for Why and Why-Not)

```json
{
  "reason_id": "rsn-44332211-00aa-bbcc-ddee-ff0011223344",
  "task_id": "2b0d7b3d-9bdd-4bad-3b7d-9b1deb4dcb6d",
  "business_key": "TASK-SMMS-0005",
  "plan_id": "f7e6d5c4-b3a2-1f0e-9d8c-7b6a5f4e3d2c",
  "decision": "UNSCHEDULED", // "SCHEDULED_OPTIMAL", "SCHEDULED_SUBOPTIMAL", "UNSCHEDULED"
  "primary_cause": "HARD_CONSTRAINT_RESOURCE_STARVATION",
  "explanation_text": "Task requires Tower Wagon TW-01 at Station Charlie, which was fully committed to higher priority statutory OHE work TASK-TDMS-0002 during available window.",
  "conflict_core": {
    "conflicting_tasks": ["TASK-TDMS-0002"],
    "conflicting_trains": [],
    "exhausted_resources": ["TW-01"]
  },
  "suggested_repair": {
    "repair_type": "SECONDARY_RESOURCE_SUBSTITUTION",
    "description": "Assign backup Tower Wagon TW-02 (available between 02:00 and 06:00 UTC) to achieve feasible assignment.",
    "is_authorized_by_policy": true
  }
}
```

---

### 2.9 PlanDiff
Represents the exact Delta between two plan revisions.

```json
{
  "diff_id": "dif-11223344-5566-7788-99aa-bbccddeeff00",
  "baseline_plan_id": "e6d5c4b3-a2f1-0e9d-8c7b-6a5f4e3d2c1b",
  "target_plan_id": "f7e6d5c4-b3a2-1f0e-9d8c-7b6a5f4e3d2c",
  "summary": {
    "tasks_unchanged": 24,
    "tasks_rescheduled": 2,
    "tasks_cancelled": 0,
    "tasks_added": 0,
    "net_corridor_availability_delta_hours": +1.5
  },
  "rescheduled_tasks": [
    {
      "task_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "business_key": "TASK-TMS-0012",
      "previous_start_utc": "2026-10-12T01:30:00Z",
      "new_start_utc": "2026-10-12T02:30:00Z",
      "shift_minutes": +60,
      "reason": "Shifted to accommodate 45-min freight forecast delay from Section Control."
    }
  ]
}
```

---

## 3. Evaluator Scenario & CRUD Contracts

To satisfy SIH evaluator live challenge requirements (where a judge adds a train, breaks a machine, or injects an emergency speed restriction), the system exposes explicit revision APIs:

### 3.1 Resource Calendar Overrides
- `POST /api/v1/corridors/{code}/resources/{resource_id}/outages`
- Body: `{"start_utc": "...", "end_utc": "...", "reason": "MACHINE_BREAKDOWN", "mode": "SYNTHETIC_SCENARIO"}`
- Automatically generates a new `Snapshot` and flags affected plans as `STALE`.

### 3.2 Train Timetable Perturbations
- `POST /api/v1/corridors/{code}/trains/{train_number}/delays`
- Body: `{"delay_minutes": 60, "location_station": "ALP", "mode": "SYNTHETIC_SCENARIO"}`
- Updates train path envelope; triggers `DISRUPTION_RECOVERY` plan evaluation.

### 3.3 Dynamic Task Injection
- `POST /api/v1/tasks`
- Ingests emergency task with `criticality: TIER_1_MANDATORY`.

---

## 4. RFC 7807 Error Response Schema

All client or server failures return a uniform JSON error payload:

```json
{
  "type": "https://samarath.railnet.gov.in/errors/resource-conflict",
  "title": "Unresolvable Hard Resource Conflict",
  "status": 409,
  "detail": "Requested task TASK-TMS-0015 conflicts with locked commitment TASK-TMS-0008 on machine BCM-01.",
  "instance": "/api/v1/plans/solve-jobs/job-1234",
  "error_code": "ERR_RESOURCE_LOCKED",
  "invalid_params": [
    {
      "name": "required_resources.resource_id",
      "reason": "Resource BCM-01 is under locked possession from 01:00 to 05:00 UTC."
    }
  ]
}
```
