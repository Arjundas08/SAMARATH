"""
Phase 17 – Resilience, Security, and Scaling Benchmarks REST API.
Blueprint Sections: 33-34, 41-43, 51, 55-58.
"""
from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone
from typing import List, Dict, Any

from app.schemas.resilience import (
    WorkloadBenchmarkSummary,
    FailureScenarioResult,
    SecurityAuditItem,
    BackupRestoreDrillReport,
    ResilienceDashboardResponse,
)
from app.engine.benchmark_harness import BenchmarkHarness
from app.engine.resilience_harness import ResilienceHarness

router = APIRouter(prefix="/resilience", tags=["Resilience & Hardening"])

# In-memory cached results for rapid dashboard loading
_cached_benchmarks: List[WorkloadBenchmarkSummary] = []
_cached_failures: List[FailureScenarioResult] = []


def _get_hardware_tag() -> str:
    import platform
    return f"{platform.machine()} Host, {platform.system()} {platform.release()}, Python {platform.python_version()} (Measured Benchmark)"


@router.get("/benchmarks", response_model=List[WorkloadBenchmarkSummary], summary="Query scaling benchmarks")
async def get_benchmarks():
    """Returns scaling benchmarks across 10, 30, 100 tasks and 300 exploratory tasks."""
    global _cached_benchmarks
    if not _cached_benchmarks:
        _cached_benchmarks = BenchmarkHarness.generate_full_benchmark_suite()
    return _cached_benchmarks


@router.post("/benchmarks/run", response_model=List[WorkloadBenchmarkSummary], summary="Execute live benchmarks")
async def run_benchmarks():
    """Runs a fresh multi-seed benchmark evaluation across declared workload envelopes."""
    global _cached_benchmarks
    _cached_benchmarks = BenchmarkHarness.generate_full_benchmark_suite()
    return _cached_benchmarks


@router.get("/failure-injection", response_model=List[FailureScenarioResult], summary="Get failure injection status")
async def get_failure_scenarios():
    """Returns the latest verified failure injection and resilience test results."""
    global _cached_failures
    if not _cached_failures:
        _cached_failures = ResilienceHarness.run_all_failure_scenarios()
    return _cached_failures


@router.post("/failure-injection/run", response_model=List[FailureScenarioResult], summary="Run live failure injections")
async def run_failure_scenarios():
    """Executes live failure injection tests (worker lease expiry, approval race, stale publications)."""
    global _cached_failures
    _cached_failures = ResilienceHarness.run_all_failure_scenarios()
    return _cached_failures


@router.get("/security/audit", response_model=List[SecurityAuditItem], summary="Get security controls audit")
async def get_security_audit():
    """Returns verifiable evidence for CSV formula safety, credential redaction, and isolation."""
    return ResilienceHarness.run_security_audit()


@router.get("/backup-drill", response_model=BackupRestoreDrillReport, summary="Execute backup/restore drill")
async def run_backup_drill():
    """Executes a real empirical backup and restoration drill and returns RPO/RTO metrics."""
    return ResilienceHarness.execute_backup_restore_drill()


@router.get("/dashboard", response_model=ResilienceDashboardResponse, summary="Comprehensive resilience dashboard")
async def get_resilience_dashboard():
    """Returns full Phase 17 Resilience, Security, and Scaling Dashboard bundle."""
    global _cached_benchmarks, _cached_failures
    if not _cached_benchmarks:
        _cached_benchmarks = BenchmarkHarness.generate_full_benchmark_suite()
    if not _cached_failures:
        _cached_failures = ResilienceHarness.run_all_failure_scenarios()

    security_items = ResilienceHarness.run_security_audit()
    drill = ResilienceHarness.execute_backup_restore_drill()

    all_benchmarks_compliant = all(b.budget_compliant for b in _cached_benchmarks if b.supported_status == "SUPPORTED_ENVELOPE")
    all_failures_passed = all(f.passed for f in _cached_failures)
    all_sec_passed = all(s.status == "VERIFIED_SAFE" for s in security_items)

    overall_status = (
        "HARDENED_AND_VERIFIED"
        if (all_benchmarks_compliant and all_failures_passed and all_sec_passed)
        else "DEGRADED"
    )

    return ResilienceDashboardResponse(
        generated_at_utc=datetime.now(timezone.utc),
        hardware_tag=_get_hardware_tag(),
        overall_status=overall_status,
        benchmarks=_cached_benchmarks,
        failure_scenarios=_cached_failures,
        security_controls=security_items,
        backup_drill=drill,
    )
