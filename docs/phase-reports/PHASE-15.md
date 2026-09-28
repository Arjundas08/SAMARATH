# Phase 15 Completion Report: Human Review, Programme Approval, and Audit Integrity

**Phase ID:** PHASE-15  
**Phase Title:** Human Review, Programme Approval, and Audit Integrity  
**Execution Date:** 2026-09-27  
**Status:** COMPLETED  
**Responsible Agent:** Antigravity Pair Programmer (Solo Build)  

---

## 1. Executive Summary

Phase 15 delivers the statutory human review, programme approval lifecycle, field-level lock governance, and append-only cryptographic audit trail for the SAMARATH railway maintenance scheduling platform in strict adherence to Blueprint Sections 27, 41-43 and SIH26027 specifications.

A central engineering priority of Phase 15 is enforcing that SAMARATH **never confuses a programme proposal approval with a real-time Railway block grant**. An approved SAMARATH programme certifies timetable feasibility and inter-departmental possession agreement; statutory track possession and traction power de-energization remain the real-time prerogative of Section Controllers via Control Office Applications and signal interlockings.

### Key Invariants Delivered & Verified:

1. **Reviewer & Approver Permissions Enforced Server-Side:**
   - Reviewing requires `PROGRAMME_REVIEW` authority (`OPERATING_REVIEWER` or `CORRIDOR_COORDINATOR`).
   - Ratification requires statutory `PROGRAMME_APPROVE` authority (`DELEGATED_APPROVER` such as Sr. DOM / ADRM).
   - Department planners without these permissions receive HTTP 403 Forbidden.
2. **Stale Version Rejection & Concurrency Protection:**
   - Every plan maintains a monotonic `version_epoch`, SHA-256 `content_hash`, and optimistic concurrency `ETag`.
   - The approval transaction re-validates the epoch, hash, and ETag inside a mutex lock before committing; concurrent mutations immediately trigger `CONCURRENT_MUTATION_DETECTED`.
3. **Independent Checker Oracle Gate:**
   - Plans without a `VALID` result from the independent mathematical checker oracle (`CHECKER_NOT_VALID`) cannot be approved.
4. **Joint Review Recommendation Binding:**
   - Approval requires at least one formal `RECOMMEND` review decision bound to the exact immutable plan content hash.
5. **Separation of Duty (Admin ≠ Approver, Self-Approval Prohibited):**
   - Infrastructure admins (`INFRASTRUCTURE_ADMIN`) cannot approve plans by virtue of administrative status (`ADMIN_CANNOT_APPROVE`).
   - An approver who is the sole recommending reviewer is prohibited from approving their own proposal (`SELF_APPROVAL_PROHIBITED`).
6. **Field-Level Lock Governance (Not Coarse Whole-Plan Booleans):**
   - Locks identify specific assignments and authority categories (`SCHEDULE_WINDOW`, `TRACK_ALLOCATION`, `RESOURCE_ASSIGNMENT`, `DURATION_ESTIMATE`, `PRIORITY_OVERRIDE`).
   - Lock revisions require audited operational justifications and bump revision counters.
7. **Append-Only Audit Trail with Hash-Chain Linkage:**
   - Audit trail is strictly append-only; **no UPDATE or DELETE endpoint exists in the application**.
   - Each event contains monotonic `chain_sequence`, `previous_event_hash`, and SHA-256 `content_hash` forming a verifiable hash chain from `GENESIS`.
8. **Statutory Evidence Export with Provenance Manifest:**
   - Generates an evidence manifest bundling plan version, checker validation, review decisions, and approval records.
   - Prominently embeds statutory disclaimer: **NEVER an official Railway block grant**.
9. **Absence of Real-Time Control Endpoints:**
   - Verified that no `/grant`, `/extension`, `/signal-control`, or `/release` endpoints exist in the system.

---

## 2. Architecture & Components

### Backend Implementation
- **Schemas (`backend/app/schemas/approval.py`):**
  - Enums: `ReviewAction`, `ApprovalAction`, `LockCategory`, `LockAuthority`, `AuditEventType`, `ApprovalBlockReason`.
  - Pydantic models: `PlanLock`, `LockCreateRequest`, `LockRevisionRequest`, `ReviewRequest`, `ReviewDecision`, `ApprovalRequest`, `ApprovalResult`, `ApprovalEligibilityCheck`, `AuditEvent`, `AuditTrailResponse`, `EvidenceExport`, `EvidenceManifestEntry`, `SubmitForReviewRequest`.
- **Engine (`backend/app/engine/approval_engine.py`):**
  - Thread-safe `ApprovalEngine` with version epoching, SHA-256 content hashing, and short ETag computation.
  - Pre-flight eligibility checking with 8 statutory gate invariants.
  - Idempotency key tracking returning duplicate responses for retried commands.
  - Append-only audit logger maintaining sequential hash-chain from `GENESIS`.
  - Field-level lock manager and evidence export bundler.
- **REST API (`backend/app/api/v1/approval.py`):**
  - `POST /api/v1/approval/register` – Plan registration.
  - `POST /api/v1/approval/submit-review` – Submit plan for joint review.
  - `POST /api/v1/approval/review` – Submit review recommendation.
  - `GET  /api/v1/approval/eligibility/{id}` – Pre-flight eligibility checklist.
  - `POST /api/v1/approval/approve` – Atomic approval transaction.
  - `POST /api/v1/approval/lock` – Create field-level lock.
  - `PUT  /api/v1/approval/lock/revise` – Revise lock with audited reason.
  - `GET  /api/v1/approval/locks/{id}` – List active locks.
  - `GET  /api/v1/approval/audit` – Query append-only audit trail.
  - `GET  /api/v1/approval/export/{id}` – Export evidence bundle.
  - `GET  /api/v1/approval/summary/{id}` – Read-only status summary.

### Frontend Implementation
- **Types (`frontend/src/types/approval.ts`):** Complete TypeScript typings matching backend schemas.
- **API Client (`frontend/src/api/approval.ts`):** Typed HTTP client for all review/approval/lock/audit endpoints.
- **View (`frontend/src/views/ApprovalView.tsx`):**
  - Signal & Slate UI with statutory notice banner.
  - Top plan status strip: Plan ID, Governance Status (`JOINT_REVIEW` / `APPROVED_PROGRAMME`), Oracle validation badge, and live Hash-Chain head with integrity verification badge.
  - 5 Interactive tabs:
    1. *Approval Cockpit*: 8 statutory freshness checks, active block inspector, and atomic ratification form with idempotency key generation.
    2. *Joint Corridor Review*: Formal review recommendation submissions (`RECOMMEND`, `REQUEST_REVISION`, `REJECT`) bound to immutable content hashes.
    3. *Field-Level Locks*: Lock creation and audited revision forms for assignments.
    4. *Append-Only Audit Trail*: Visual timeline with previous/current SHA-256 hash linkage.
    5. *Evidence Package*: Cryptographic provenance manifest viewer with JSON download.
- **Navigation Integration:** Added to `AppShell.tsx` and routed in `App.tsx`.

---

## 3. Automated Test Verification

**Test Suite:** `backend/tests/test_phase15_approval.py`  
**Phase 15 Test Results:** **26 passed / 26 total (100%) in 2.51s**  
**Full System Regression Suite:** **165 passed / 165 total (100%) in 68.51s across all 15 phases**

### Phase 15 Acceptance Test Results:

| Test Name | Acceptance Criteria Verified | Status |
|:---|:---|:---:|
| `test_planner_cannot_review` | Department planner cannot submit reviews (403 Forbidden) | **PASSED** |
| `test_reviewer_can_review` | Operating reviewer can submit recommendations (200 OK) | **PASSED** |
| `test_planner_cannot_access_audit` | Unprivileged role cannot access audit log (403 Forbidden) | **PASSED** |
| `test_stale_epoch_blocks_approval` | Stale expected version epoch blocks approval | **PASSED** |
| `test_race_between_validation_and_approval` | External mutation between read and commit blocks transaction | **PASSED** |
| `test_invalid_checker_blocks_approval` | Unvalidated plan blocked by CHECKER_NOT_VALID | **PASSED** |
| `test_no_recommendation_blocks_approval` | Missing review recommendation blocks approval | **PASSED** |
| `test_audit_trail_grows_monotonically` | Every state mutation appends a sequential audit event | **PASSED** |
| `test_no_delete_endpoint_exists` | Proves no DELETE/mutation endpoint exists for audit trail | **PASSED** |
| `test_duplicate_idempotency_key_returns_same_result` | Duplicate submission returns identical result without double-execution | **PASSED** |
| `test_chain_integrity_verified` | Sequential SHA-256 hash chain verified from GENESIS | **PASSED** |
| `test_events_have_content_hashes` | Every audit event contains a 64-character hex digest | **PASSED** |
| `test_summary_is_read_only` | Plan metrics summary cannot be mutated via HTTP | **PASSED** |
| `test_admin_approval_rejected` | Infrastructure admin rejected with ADMIN_CANNOT_APPROVE | **PASSED** |
| `test_sole_reviewer_approver_blocked` | Self-approval prohibited with SELF_APPROVAL_PROHIBITED | **PASSED** |
| `test_create_lock` | Assignment-level lock created with audited category & reason | **PASSED** |
| `test_revise_lock` | Lock revision increments counter and records new justification | **PASSED** |
| `test_locks_are_per_assignment` | Locks apply per assignment ID, not whole-plan boolean | **PASSED** |
| `test_export_contains_disclaimer` | Export bundle contains statutory non-grant disclaimer | **PASSED** |
| `test_export_has_manifest` | Export contains plan, checker, review, and approval entries | **PASSED** |
| `test_export_has_provenance` | Export metadata includes provenance mode, timestamps, and hashes | **PASSED** |
| `test_no_grant_endpoint` | Proves `/api/v1/approval/grant` does NOT exist (404) | **PASSED** |
| `test_no_release_endpoint` | Proves `/api/v1/approval/release` does NOT exist (404) | **PASSED** |
| `test_no_signal_control_endpoint` | Proves `/api/v1/approval/signal-control` does NOT exist (404) | **PASSED** |
| `test_full_approval_lifecycle` | End-to-end register → review → approve lifecycle | **PASSED** |
| `test_rejection_resets_to_draft` | Rejection transitions plan back to DRAFT_PROPOSAL | **PASSED** |

---

## 4. UI Browser Verification

Browser verification was completed autonomously using Playwright browser subagent.  
- **Recording Artifact:** `approval_ui_verification_-62135596800000.webp`  
- **Verified Viewport & Elements:**
  - Header with `Phase 15` badge.
  - Prominent amber statutory notice banner emphasizing proposal vs real-time block grant boundary.
  - 4 status metrics cards (Plan Identifier, Governance Status, Independent Oracle, Hash-Chain Head).
  - All 5 interactive tabs loaded and rendered without console or DOM errors.
  - Joint review recommendation form and active field locks rendered and tested.

---

## 5. Phase Sign-Off & Status

Phase 15 is **COMPLETE and FULLY VERIFIED**. All statutory invariants, separation-of-duty controls, append-only hash chains, and user interface workflows are operating cleanly in production-equivalent configuration.
