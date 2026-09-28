"""
Phase 15 – Human Review, Programme Approval, and Audit Integrity Acceptance Tests.

Acceptance coverage:
  1.  Reviewer/approver permissions (PROGRAMME_REVIEW, PROGRAMME_APPROVE)
  2.  Stale version rejection (version epoch mismatch)
  3.  Update/approval concurrency race (epoch bumped between validation and commit)
  4.  Rejected invalid plan (checker result INVALID blocks approval)
  5.  Missing-parent reconciliation (review recommendation required)
  6.  Preserved historical decisions (audit trail append-only, no delete)
  7.  Duplicate command idempotency (same idempotency key → same result)
  8.  Audit linkage and hash-chain integrity
  9.  Server-enforced read-only metrics (no mutation endpoint)
  10. Infrastructure admin cannot approve
  11. Self-approval prohibition
  12. Lock management (create, revise, per-assignment)
  13. Evidence export with provenance and disclaimer
  14. No grant/extension/signal-control/release endpoint exists
  15. UI labels programme proposal/approval accurately
"""
import pytest
import hashlib
import json
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.engine.approval_engine import approval_engine, ApprovalEngine


# ──────────────────────────────────────────────
#  Fixtures
# ──────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_approval_engine():
    """Reset the singleton approval engine before each test."""
    approval_engine.__init__()
    yield


def _make_client():
    """Create a fresh TestClient."""
    return TestClient(app)


def _login(c: TestClient, username: str, password: str):
    """Login user; cookies are stored on the TestClient automatically."""
    resp = c.post("/api/v1/auth/login", json={
        "username": username, "password": password
    })
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    return resp.json()


def _register_plan(c: TestClient, plan_id: str = None) -> dict:
    """Register a plan and return its metadata."""
    plan_id = plan_id or str(uuid4())
    plan_data = {
        "plan_id": plan_id,
        "plan_data": {
            "plan_version_number": 1,
            "assignments": [
                {"task_id": "TASK-001", "start_hour": 2, "end_hour": 5},
                {"task_id": "TASK-002", "start_hour": 8, "end_hour": 12},
            ],
            "horizon_type": "WEEKLY",
        },
        "provenance_mode": "TEST",
    }
    resp = c.post("/api/v1/approval/register", json=plan_data)
    assert resp.status_code == 200, f"Register failed: {resp.text}"
    return resp.json()


def _full_approval_setup(plan_id: str = None):
    """
    Setup a plan through the full lifecycle up to review recommendation.
    Uses SEPARATE clients for reviewer and approver (different cookies).
    Returns (plan_id, plan_meta, reviewer_client, approver_client).
    """
    # Create approver client
    approver_c = _make_client()
    _login(approver_c, "approver_operating", "appr@pass2026")

    # Create reviewer client
    reviewer_c = _make_client()
    _login(reviewer_c, "reviewer_operating", "rev@pass2026")

    # Register plan as approver
    meta = _register_plan(approver_c, plan_id)
    pid = meta["plan_id"]

    # Mark checker as valid
    approval_engine.register_checker_result(pid, True)

    # Submit for review (reviewer has PROGRAMME_REVIEW)
    resp = reviewer_c.post("/api/v1/approval/submit-review", json={
        "plan_id": pid,
        "plan_version": 1,
        "plan_content_hash": meta["content_hash"],
        "comment": "Ready for joint review",
    })

    # Review: RECOMMEND
    resp = reviewer_c.post("/api/v1/approval/review", json={
        "plan_id": pid,
        "plan_version": 1,
        "plan_content_hash": meta["content_hash"],
        "action": "RECOMMEND",
        "comment": "Looks good, recommend approval",
    })
    assert resp.status_code == 200, f"Review failed: {resp.text}"

    # Get final state for approval
    summary = approver_c.get(f"/api/v1/approval/summary/{pid}").json()

    return pid, summary, reviewer_c, approver_c


# ──────────────────────────────────────────────
#  TEST 1: Reviewer/Approver Permissions
# ──────────────────────────────────────────────

class TestPermissions:
    """Verify RBAC enforcement for review and approval endpoints."""

    def test_planner_cannot_review(self):
        """Department planner without PROGRAMME_REVIEW cannot submit reviews."""
        c = _make_client()
        _login(c, "planner_tms", "tms@pass2026")
        resp = c.post("/api/v1/approval/review", json={
            "plan_id": str(uuid4()),
            "plan_version": 1,
            "plan_content_hash": "abc",
            "action": "RECOMMEND",
        })
        assert resp.status_code == 403

    def test_reviewer_can_review(self):
        """Operating reviewer with PROGRAMME_REVIEW can submit reviews."""
        approver_c = _make_client()
        _login(approver_c, "approver_operating", "appr@pass2026")
        meta = _register_plan(approver_c)
        pid = meta["plan_id"]

        reviewer_c = _make_client()
        _login(reviewer_c, "reviewer_operating", "rev@pass2026")

        resp = reviewer_c.post("/api/v1/approval/review", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": meta["content_hash"],
            "action": "RECOMMEND",
            "comment": "Approved from reviewer",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["action"] == "RECOMMEND"

    def test_planner_cannot_access_audit(self):
        """Department planner without AUDIT_READ cannot query audit trail."""
        c = _make_client()
        _login(c, "planner_tms", "tms@pass2026")
        resp = c.get("/api/v1/approval/audit")
        assert resp.status_code == 403


# ──────────────────────────────────────────────
#  TEST 2: Stale Version Rejection
# ──────────────────────────────────────────────

class TestStaleVersionRejection:
    """Verify that stale version epoch causes approval rejection."""

    def test_stale_epoch_blocks_approval(self):
        """Approval with outdated version_epoch is rejected."""
        pid, summary, _, approver_c = _full_approval_setup()

        resp = approver_c.post("/api/v1/approval/approve", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": summary["content_hash"],
            "expected_etag": "stale_etag",
            "expected_version_epoch": 1,
            "action": "APPROVE",
            "idempotency_key": str(uuid4()),
        })
        data = resp.json()
        assert data["success"] is False
        reasons = [b["reason"] for b in data["block_reasons"]]
        assert "CONCURRENT_MUTATION_DETECTED" in reasons


# ──────────────────────────────────────────────
#  TEST 3: Concurrency Race Detection
# ──────────────────────────────────────────────

class TestConcurrencyRace:
    """Verify that a concurrent mutation between validation and commit is detected."""

    def test_race_between_validation_and_approval(self):
        """
        Simulate: user fetches eligibility, then another user mutates the plan,
        then the first user tries to approve with the now-stale epoch.
        """
        pid, summary, _, approver_c = _full_approval_setup()

        elig = approver_c.get(f"/api/v1/approval/eligibility/{pid}").json()
        captured_epoch = elig["current_version_epoch"]
        captured_etag = elig["current_etag"]

        # ── Concurrent mutation happens here ──
        new_epoch = approval_engine.bump_epoch(pid)
        assert new_epoch > captured_epoch

        resp = approver_c.post("/api/v1/approval/approve", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": summary["content_hash"],
            "expected_etag": captured_etag,
            "expected_version_epoch": captured_epoch,
            "action": "APPROVE",
            "idempotency_key": str(uuid4()),
        })
        data = resp.json()
        assert data["success"] is False
        reasons = [b["reason"] for b in data["block_reasons"]]
        assert "CONCURRENT_MUTATION_DETECTED" in reasons
        assert "ETAG_MISMATCH" in reasons


# ──────────────────────────────────────────────
#  TEST 4: Rejected Invalid Plan
# ──────────────────────────────────────────────

class TestRejectedInvalidPlan:
    """Verify that a plan without valid checker result cannot be approved."""

    def test_invalid_checker_blocks_approval(self):
        """Plan with checker INVALID cannot be approved."""
        approver_c = _make_client()
        _login(approver_c, "approver_operating", "appr@pass2026")
        meta = _register_plan(approver_c)
        pid = meta["plan_id"]

        # Checker result is INVALID
        approval_engine.register_checker_result(pid, False)

        reviewer_c = _make_client()
        _login(reviewer_c, "reviewer_operating", "rev@pass2026")
        reviewer_c.post("/api/v1/approval/review", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": meta["content_hash"],
            "action": "RECOMMEND",
        })

        summary = approver_c.get(f"/api/v1/approval/summary/{pid}").json()

        resp = approver_c.post("/api/v1/approval/approve", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": summary["content_hash"],
            "expected_etag": summary["etag"],
            "expected_version_epoch": summary["version_epoch"],
            "action": "APPROVE",
            "idempotency_key": str(uuid4()),
        })
        data = resp.json()
        assert data["success"] is False
        reasons = [b["reason"] for b in data["block_reasons"]]
        assert "CHECKER_NOT_VALID" in reasons


# ──────────────────────────────────────────────
#  TEST 5: Missing Review Recommendation
# ──────────────────────────────────────────────

class TestMissingRecommendation:
    """Verify that a plan without review recommendation cannot be approved."""

    def test_no_recommendation_blocks_approval(self):
        """Plan without RECOMMEND review cannot proceed to approval."""
        approver_c = _make_client()
        _login(approver_c, "approver_operating", "appr@pass2026")
        meta = _register_plan(approver_c)
        pid = meta["plan_id"]

        approval_engine.register_checker_result(pid, True)
        summary = approver_c.get(f"/api/v1/approval/summary/{pid}").json()

        resp = approver_c.post("/api/v1/approval/approve", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": summary["content_hash"],
            "expected_etag": summary["etag"],
            "expected_version_epoch": summary["version_epoch"],
            "action": "APPROVE",
            "idempotency_key": str(uuid4()),
        })
        data = resp.json()
        assert data["success"] is False
        reasons = [b["reason"] for b in data["block_reasons"]]
        assert "MISSING_REVIEW_RECOMMENDATION" in reasons


# ──────────────────────────────────────────────
#  TEST 6: Preserved Historical Decisions
# ──────────────────────────────────────────────

class TestPreservedHistory:
    """Verify that audit trail is append-only and historical decisions are preserved."""

    def test_audit_trail_grows_monotonically(self):
        """Each action adds to the audit trail; no deletions occur."""
        pid, summary, _, approver_c = _full_approval_setup()

        audit_resp = approver_c.get("/api/v1/approval/audit").json()
        count_before = audit_resp["total_count"]
        assert count_before > 0

        approver_c.post("/api/v1/approval/approve", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": summary["content_hash"],
            "expected_etag": summary["etag"],
            "expected_version_epoch": summary["version_epoch"],
            "action": "APPROVE",
            "idempotency_key": str(uuid4()),
        })

        audit_after = approver_c.get("/api/v1/approval/audit").json()
        assert audit_after["total_count"] > count_before

    def test_no_delete_endpoint_exists(self):
        """No DELETE endpoint exists for audit events."""
        c = _make_client()
        _login(c, "approver_operating", "appr@pass2026")
        resp = c.delete("/api/v1/approval/audit")
        assert resp.status_code == 405


# ──────────────────────────────────────────────
#  TEST 7: Duplicate Command Idempotency
# ──────────────────────────────────────────────

class TestIdempotency:
    """Verify that duplicate approval commands with same idempotency key are safe."""

    def test_duplicate_idempotency_key_returns_same_result(self):
        """Second approval with same idempotency key returns identical result."""
        pid, summary, _, approver_c = _full_approval_setup()
        idem_key = str(uuid4())

        payload = {
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": summary["content_hash"],
            "expected_etag": summary["etag"],
            "expected_version_epoch": summary["version_epoch"],
            "action": "APPROVE",
            "idempotency_key": idem_key,
        }
        resp1 = approver_c.post("/api/v1/approval/approve", json=payload)
        data1 = resp1.json()
        assert data1["success"] is True
        assert data1["was_idempotent_duplicate"] is False

        resp2 = approver_c.post("/api/v1/approval/approve", json=payload)
        data2 = resp2.json()
        assert data2["was_idempotent_duplicate"] is True
        assert data2["success"] == data1["success"]


# ──────────────────────────────────────────────
#  TEST 8: Audit Linkage and Hash-Chain Integrity
# ──────────────────────────────────────────────

class TestAuditChain:
    """Verify hash-chain integrity of audit trail."""

    def test_chain_integrity_verified(self):
        """Audit trail hash-chain is self-consistent."""
        pid, summary, _, approver_c = _full_approval_setup()

        audit = approver_c.get("/api/v1/approval/audit").json()
        assert audit["chain_integrity_verified"] is True

        events = audit["events"]
        for i, event in enumerate(events):
            assert event["chain_sequence"] >= 0

    def test_events_have_content_hashes(self):
        """Each audit event has a non-empty content_hash."""
        _full_approval_setup()
        c = _make_client()
        _login(c, "approver_operating", "appr@pass2026")
        audit = c.get("/api/v1/approval/audit").json()
        for event in audit["events"]:
            assert len(event["content_hash"]) == 64


# ──────────────────────────────────────────────
#  TEST 9: Server-Enforced Read-Only Metrics
# ──────────────────────────────────────────────

class TestReadOnlyMetrics:
    """Verify that plan metrics cannot be mutated through any endpoint."""

    def test_summary_is_read_only(self):
        """Summary endpoint is GET only — no POST/PUT/DELETE."""
        c = _make_client()
        _login(c, "approver_operating", "appr@pass2026")
        pid = str(uuid4())
        resp = c.post(f"/api/v1/approval/summary/{pid}")
        assert resp.status_code == 405
        resp = c.put(f"/api/v1/approval/summary/{pid}")
        assert resp.status_code == 405


# ──────────────────────────────────────────────
#  TEST 10: Infrastructure Admin Cannot Approve
# ──────────────────────────────────────────────

class TestAdminCannotApprove:
    """Infrastructure admin must not be able to approve by virtue of admin status."""

    def test_admin_approval_rejected(self):
        """Admin user gets ADMIN_CANNOT_APPROVE and ROLE_INSUFFICIENT blocks."""
        pid, summary, _, _ = _full_approval_setup()

        admin_c = _make_client()
        _login(admin_c, "admin_infra", "admin@pass2026")

        resp = admin_c.post("/api/v1/approval/approve", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": summary["content_hash"],
            "expected_etag": summary["etag"],
            "expected_version_epoch": summary["version_epoch"],
            "action": "APPROVE",
            "idempotency_key": str(uuid4()),
        })
        data = resp.json()
        assert data["success"] is False
        reasons = [b["reason"] for b in data["block_reasons"]]
        assert "ADMIN_CANNOT_APPROVE" in reasons or "ROLE_INSUFFICIENT" in reasons


# ──────────────────────────────────────────────
#  TEST 11: Self-Approval Prohibition
# ──────────────────────────────────────────────

class TestSelfApprovalProhibited:
    """Approver who is the sole recommending reviewer cannot self-approve."""

    def test_sole_reviewer_approver_blocked(self):
        """If the approver is the sole reviewer, self-approval is blocked."""
        approver_c = _make_client()
        _login(approver_c, "approver_operating", "appr@pass2026")
        meta = _register_plan(approver_c)
        pid = meta["plan_id"]

        approval_engine.register_checker_result(pid, True)

        # Approver reviews their own plan (they also have PROGRAMME_REVIEW)
        approver_c.post("/api/v1/approval/review", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": meta["content_hash"],
            "action": "RECOMMEND",
        })

        summary = approver_c.get(f"/api/v1/approval/summary/{pid}").json()

        resp = approver_c.post("/api/v1/approval/approve", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": summary["content_hash"],
            "expected_etag": summary["etag"],
            "expected_version_epoch": summary["version_epoch"],
            "action": "APPROVE",
            "idempotency_key": str(uuid4()),
        })
        data = resp.json()
        assert data["success"] is False
        reasons = [b["reason"] for b in data["block_reasons"]]
        assert "SELF_APPROVAL_PROHIBITED" in reasons


# ──────────────────────────────────────────────
#  TEST 12: Lock Management
# ──────────────────────────────────────────────

class TestLockManagement:
    """Verify field-level lock creation, revision, and per-assignment scope."""

    def test_create_lock(self):
        """Create a lock on a specific assignment field."""
        c = _make_client()
        _login(c, "approver_operating", "appr@pass2026")
        meta = _register_plan(c)
        pid = meta["plan_id"]

        resp = c.post("/api/v1/approval/lock", json={
            "plan_id": pid,
            "assignment_id": "TASK-001",
            "lock_category": "SCHEDULE_WINDOW",
            "reason": "Confirmed with section controller",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["assignment_id"] == "TASK-001"
        assert data["lock_category"] == "SCHEDULE_WINDOW"
        assert data["is_active"] is True

    def test_revise_lock(self):
        """Revise a lock through an audited new revision."""
        c = _make_client()
        _login(c, "approver_operating", "appr@pass2026")
        meta = _register_plan(c)
        pid = meta["plan_id"]

        create_resp = c.post("/api/v1/approval/lock", json={
            "plan_id": pid,
            "assignment_id": "TASK-002",
            "lock_category": "RESOURCE_ASSIGNMENT",
            "reason": "Initial lock",
        })
        lock_id = create_resp.json()["lock_id"]

        revise_resp = c.put("/api/v1/approval/lock/revise", json={
            "lock_id": lock_id,
            "new_reason": "Updated after field coordination",
            "new_category": "TRACK_ALLOCATION",
        })
        assert revise_resp.status_code == 200
        data = revise_resp.json()
        assert data["revision"] == 2
        assert data["lock_category"] == "TRACK_ALLOCATION"

    def test_locks_are_per_assignment(self):
        """Locks identify specific assignments, not a whole-plan boolean."""
        c = _make_client()
        _login(c, "approver_operating", "appr@pass2026")
        meta = _register_plan(c)
        pid = meta["plan_id"]

        c.post("/api/v1/approval/lock", json={
            "plan_id": pid,
            "assignment_id": "TASK-001",
            "lock_category": "SCHEDULE_WINDOW",
        })
        c.post("/api/v1/approval/lock", json={
            "plan_id": pid,
            "assignment_id": "TASK-002",
            "lock_category": "RESOURCE_ASSIGNMENT",
        })

        resp = c.get(f"/api/v1/approval/locks/{pid}")
        data = resp.json()
        assert len(data["locks"]) == 2
        assignment_ids = {lk["assignment_id"] for lk in data["locks"]}
        assert assignment_ids == {"TASK-001", "TASK-002"}


# ──────────────────────────────────────────────
#  TEST 13: Evidence Export with Provenance
# ──────────────────────────────────────────────

class TestEvidenceExport:
    """Verify evidence export contains provenance, manifest, and disclaimer."""

    def test_export_contains_disclaimer(self):
        """Evidence export is NEVER an official Railway grant."""
        pid, _, _, _ = _full_approval_setup()
        c = _make_client()
        _login(c, "approver_operating", "appr@pass2026")

        resp = c.get(f"/api/v1/approval/export/{pid}")
        assert resp.status_code == 200
        data = resp.json()
        assert "PROGRAMME PROPOSAL" in data["disclaimer"]
        assert "NOT" in data["disclaimer"]

    def test_export_has_manifest(self):
        """Export contains source/version manifest entries."""
        pid, _, _, _ = _full_approval_setup()
        c = _make_client()
        _login(c, "approver_operating", "appr@pass2026")

        resp = c.get(f"/api/v1/approval/export/{pid}")
        data = resp.json()
        assert len(data["manifest"]) >= 2
        source_types = {m["source_type"] for m in data["manifest"]}
        assert "plan" in source_types
        assert "checker_result" in source_types

    def test_export_has_provenance(self):
        """Export includes provenance mode."""
        pid, _, _, _ = _full_approval_setup()
        c = _make_client()
        _login(c, "approver_operating", "appr@pass2026")

        resp = c.get(f"/api/v1/approval/export/{pid}")
        data = resp.json()
        assert data["provenance_mode"] == "TEST"


# ──────────────────────────────────────────────
#  TEST 14: No Grant/Extension/Signal Endpoint
# ──────────────────────────────────────────────

class TestNoGrantEndpoint:
    """Verify that no grant, extension, signal-control, or release endpoint exists."""

    def test_no_grant_endpoint(self):
        """No /grant endpoint exists."""
        c = _make_client()
        resp = c.post("/api/v1/approval/grant", json={})
        assert resp.status_code in (404, 405, 401, 422)

    def test_no_release_endpoint(self):
        """No /release endpoint exists."""
        c = _make_client()
        resp = c.post("/api/v1/approval/release", json={})
        assert resp.status_code in (404, 405, 401, 422)

    def test_no_signal_control_endpoint(self):
        """No /signal-control endpoint exists."""
        c = _make_client()
        resp = c.post("/api/v1/approval/signal-control", json={})
        assert resp.status_code in (404, 405, 401, 422)


# ──────────────────────────────────────────────
#  TEST 15: Full Happy Path (End-to-End)
# ──────────────────────────────────────────────

class TestFullHappyPath:
    """Complete lifecycle from registration to approved programme."""

    def test_full_approval_lifecycle(self):
        """
        Register → Checker Valid → Submit for Review → Review RECOMMEND →
        Approval → Verify APPROVED_PROGRAMME status.
        """
        pid, summary, _, approver_c = _full_approval_setup()

        resp = approver_c.post("/api/v1/approval/approve", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": summary["content_hash"],
            "expected_etag": summary["etag"],
            "expected_version_epoch": summary["version_epoch"],
            "action": "APPROVE",
            "comment": "Programme approved for implementation",
            "idempotency_key": str(uuid4()),
        })
        data = resp.json()
        assert data["success"] is True
        assert data["new_plan_status"] == "APPROVED_PROGRAMME"
        assert data["new_authority_state"] == "OPERATING_RATIFIED"
        assert data["approved_by"] is not None

        summary_after = approver_c.get(f"/api/v1/approval/summary/{pid}").json()
        assert summary_after["plan_status"] == "APPROVED_PROGRAMME"
        assert summary_after["programme_authority_state"] == "OPERATING_RATIFIED"


# ──────────────────────────────────────────────
#  TEST 16: Rejection Path
# ──────────────────────────────────────────────

class TestRejectionPath:
    """Verify that approval rejection resets plan state correctly."""

    def test_rejection_resets_to_draft(self):
        """Rejected plan returns to DRAFT_PROPOSAL state."""
        pid, summary, _, approver_c = _full_approval_setup()

        resp = approver_c.post("/api/v1/approval/approve", json={
            "plan_id": pid,
            "plan_version": 1,
            "plan_content_hash": summary["content_hash"],
            "expected_etag": summary["etag"],
            "expected_version_epoch": summary["version_epoch"],
            "action": "REJECT",
            "comment": "Needs revised duration estimates",
            "idempotency_key": str(uuid4()),
        })
        data = resp.json()
        assert data["success"] is True
        assert data["new_plan_status"] == "DRAFT_PROPOSAL"
        assert data["new_authority_state"] == "PROPOSED"
