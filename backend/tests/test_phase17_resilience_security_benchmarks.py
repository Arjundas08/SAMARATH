"""
Phase 17 – Resilience, Security, and Scaling Evidence Acceptance Tests.
Blueprint Sections: 28, 31, 33-34, 41-43, 51, 55-58.

Acceptance Coverage:
1. Formula injection neutralization in CSV exports.
2. Log and credential redaction.
3. Territory and role isolation guards.
4. Offline self-contained compliance.
5. Worker lease expiration and fencing token publication rejection.
6. Approval concurrency race detection and stale version epoch rejection.
7. Snapshot obsolescence publication abort.
8. Idempotency retry storms with shared idempotency keys.
9. RFC 7807 malformed record quarantine isolation.
10. Backup and restore drill with RPO/RTO verification.
11. Multi-seed scaling benchmark execution and budget compliance.
12. Comprehensive REST API endpoint integration.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security_sanitizer import (
    sanitize_csv_cell,
    sanitize_csv_row,
    redact_sensitive_data,
    TerritoryIsolationGuard,
    OfflineIntegrityVerifier,
)
from app.engine.resilience_harness import ResilienceHarness
from app.engine.benchmark_harness import BenchmarkHarness


@pytest.fixture
def client():
    return TestClient(app)


# ──────────────────────────────────────────────
#  1. Security Controls & Sanitization
# ──────────────────────────────────────────────

class TestSecuritySanitization:
    def test_formula_injection_sanitization(self):
        """Verifies Excel/CSV formula injection triggers are escaped with single quote."""
        malicious_cells = [
            "=cmd|' /C calc'!A0",
            "+12345",
            "-SUM(A1:A10)",
            "@HYPERLINK('http://evil.com')",
            "\tTAB_INJECTION",
            "\rRETURN_INJECTION",
            "   =SPACED_FORMULA",
        ]
        for cell in malicious_cells:
            sanitized = sanitize_csv_cell(cell)
            assert sanitized.startswith("'"), f"Cell '{cell}' was not neutralized: '{sanitized}'"

        # Safe values should not have single quotes prepended
        safe_cells = ["NORMAL_TASK_001", "VKC-UP-LINE", "120", "2026-10-12T02:00:00Z"]
        for cell in safe_cells:
            sanitized = sanitize_csv_cell(cell)
            assert not sanitized.startswith("'"), f"Safe cell '{cell}' was wrongly escaped: '{sanitized}'"

        # Row sanitization
        row = ["TASK-001", "=2+2", "TRACK-UP", "@EVIL"]
        sanitized_row = sanitize_csv_row(row)
        assert sanitized_row[0] == "TASK-001"
        assert sanitized_row[1] == "'=2+2"
        assert sanitized_row[2] == "TRACK-UP"
        assert sanitized_row[3] == "'@EVIL"

    def test_log_and_credential_redaction(self):
        """Verifies recursive credential redaction prevents secrets leaking into logs."""
        payload = {
            "username": "reviewer_operating",
            "password_hash": "$2b$12$eX4mP1eH4shV4lu3",
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.t-ID",
            "nested": {
                "auth_header": "Bearer secret_token_xyz",
                "normal_field": "VKC_CORRIDOR",
            },
            "array_items": [
                {"cookie": "samarath_session=xyz"},
                {"task_id": "TASK-001"},
            ],
        }
        redacted = redact_sensitive_data(payload)

        assert redacted["password_hash"] == "[REDACTED_CREDENTIAL]"
        assert redacted["access_token"] == "[REDACTED_CREDENTIAL]"
        assert redacted["nested"]["auth_header"] == "[REDACTED_CREDENTIAL]"
        assert redacted["nested"]["normal_field"] == "VKC_CORRIDOR"
        assert redacted["array_items"][0]["cookie"] == "[REDACTED_CREDENTIAL]"
        assert redacted["array_items"][1]["task_id"] == "TASK-001"

    def test_territory_isolation(self):
        """Verifies territory boundaries prevent cross-division access."""
        # Scoped to VKC
        assert TerritoryIsolationGuard.is_territory_allowed("VKC", "VKC") is True
        assert TerritoryIsolationGuard.is_territory_allowed("VKC", "MDU") is False
        assert TerritoryIsolationGuard.is_territory_allowed("VKC", "SBC") is False

        # HQ user (territory None) can access any corridor
        assert TerritoryIsolationGuard.is_territory_allowed(None, "VKC") is True
        assert TerritoryIsolationGuard.is_territory_allowed(None, "MDU") is True

    def test_offline_integrity(self):
        """Verifies zero reliance on remote AI or CDN endpoints."""
        safe_str = "Local CP-SAT optimizer running against PostgreSQL schema."
        assert OfflineIntegrityVerifier.verify_no_external_endpoints(safe_str) is True

        unsafe_str = "Connecting to https://api.openai.com/v1/chat/completions"
        assert OfflineIntegrityVerifier.verify_no_external_endpoints(unsafe_str) is False


# ──────────────────────────────────────────────
#  2. Failure Injection & Resilience
# ──────────────────────────────────────────────

class TestFailureInjection:
    def test_worker_lease_fencing(self):
        """Scenario 1: Leased worker crash, lease expiry, and stale publication rejection."""
        result = ResilienceHarness.test_worker_lease_expiration_and_fencing()
        assert result.passed is True
        assert "StaleWorkerPublicationError" in result.observed_outcome

    def test_approval_concurrency_race(self):
        """Scenario 2: Concurrent approval transactions on same epoch."""
        result = ResilienceHarness.test_approval_concurrency_race()
        assert result.passed is True
        assert "Racer 1 ratified plan; Racer 2 rejected" in result.observed_outcome

    def test_stale_run_publication_rejection(self):
        """Scenario 3: Snapshot obsolescence aborts publication."""
        result = ResilienceHarness.test_stale_run_publication_rejection()
        assert result.passed is True

    def test_idempotency_retry_storm(self):
        """Scenario 4: Burst duplicate commands with shared idempotency key."""
        result = ResilienceHarness.test_idempotency_retry_storm()
        assert result.passed is True

    def test_quarantine_partial_batch_failure(self):
        """Scenario 5: Malformed records isolated without batch failure."""
        result = ResilienceHarness.test_quarantine_partial_batch_failure()
        assert result.passed is True


# ──────────────────────────────────────────────
#  3. Backup & Restore Drill
# ──────────────────────────────────────────────

class TestBackupRestoreDrill:
    def test_backup_restore_drill(self):
        """Verifies empirical backup/restore drill achieves zero data loss."""
        drill = ResilienceHarness.execute_backup_restore_drill()
        assert drill.integrity_hash_matched is True
        assert drill.rpo_seconds == 0.0
        assert drill.rto_seconds < 1.0
        assert drill.status == "DRILL_PASSED_ZERO_DATA_LOSS"
        assert drill.offline_verified is True


# ──────────────────────────────────────────────
#  4. Scaling Benchmarks
# ──────────────────────────────────────────────

class TestScalingBenchmarks:
    def test_single_benchmark_run(self):
        """Tests instrumented execution of 10 tasks with phase metrics and memory tracking."""
        metrics = BenchmarkHarness.run_single_benchmark(num_tasks=10, seed=42, time_limit_sec=10.0)
        assert metrics.total_tasks == 10
        assert metrics.scheduled_tasks > 0
        assert metrics.candidate_gen_ms >= 0.0
        assert metrics.solve_time_ms >= 0.0
        assert metrics.checker_verify_ms >= 0.0
        assert metrics.peak_memory_mb >= 0.0
        assert metrics.checker_passed is True

    def test_workload_evaluation_30_tasks(self):
        """Tests 30-task benchmark against Blueprint Section 17 30s budget."""
        summary = BenchmarkHarness.evaluate_workload(num_tasks=30, seeds=[42])
        assert summary.workload_tasks == 30
        assert summary.sample_count == 1
        assert summary.budget_target_ms == 30000.0
        assert summary.budget_compliant is True
        assert summary.checker_pass_rate_pct == 100.0


# ──────────────────────────────────────────────
#  5. REST API Integration
# ──────────────────────────────────────────────

class TestResilienceAPI:
    def test_get_dashboard(self, client):
        """GET /api/v1/resilience/dashboard returns comprehensive dashboard bundle."""
        resp = client.get("/api/v1/resilience/dashboard")
        assert resp.status_code == 200
        data = resp.json()
        assert "overall_status" in data
        assert len(data["benchmarks"]) >= 3
        assert len(data["failure_scenarios"]) == 5
        assert len(data["security_controls"]) == 4
        assert data["backup_drill"]["integrity_hash_matched"] is True

    def test_get_failure_injection(self, client):
        """GET /api/v1/resilience/failure-injection returns failure test results."""
        resp = client.get("/api/v1/resilience/failure-injection")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 5
        assert all(it["passed"] is True for it in items)

    def test_get_security_audit(self, client):
        """GET /api/v1/resilience/security/audit returns security controls."""
        resp = client.get("/api/v1/resilience/security/audit")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 4
        assert all(it["status"] == "VERIFIED_SAFE" for it in items)

    def test_get_backup_drill(self, client):
        """GET /api/v1/resilience/backup-drill returns drill report."""
        resp = client.get("/api/v1/resilience/backup-drill")
        assert resp.status_code == 200
        drill = resp.json()
        assert drill["status"] == "DRILL_PASSED_ZERO_DATA_LOSS"
