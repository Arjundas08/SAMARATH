"""
Phase 17 – Resilience, Security, and Scaling Benchmark Schemas.
Blueprint Sections: 33-34, 41-43, 51, 55-58.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import Field
from app.schemas.common import APIModel


class BenchmarkStageMetrics(APIModel):
    """Execution latency breakdown across planning pipeline stages."""
    candidate_gen_ms: float = Field(..., description="Opportunity / candidate generation latency in milliseconds")
    model_construction_ms: float = Field(..., description="CP-SAT variable and constraint construction latency in milliseconds")
    solve_time_ms: float = Field(..., description="CP-SAT optimization solve latency in milliseconds")
    checker_verify_ms: float = Field(..., description="Independent feasibility oracle validation latency in milliseconds")
    total_roundtrip_ms: float = Field(..., description="Total pipeline execution latency in milliseconds")
    peak_memory_mb: float = Field(..., description="Peak memory allocated during run in MB")
    scheduled_tasks: int = Field(..., description="Count of tasks scheduled")
    total_tasks: int = Field(..., description="Total tasks in workload")
    checker_passed: bool = Field(..., description="Whether independent oracle certified schedule feasibility")


class WorkloadBenchmarkSummary(APIModel):
    """Statistical summary across multiple seeds for a declared workload size."""
    workload_tasks: int = Field(..., description="Task count: 10, 30, 100, or 300 exploratory")
    sample_count: int = Field(..., description="Number of independent seed evaluations")
    seeds_tested: List[int] = Field(..., description="Random seeds tested")
    p50_total_ms: float = Field(..., description="Median (P50) total latency in milliseconds")
    p95_total_ms: float = Field(..., description="Tail (P95) total latency in milliseconds")
    mean_solve_ms: float = Field(..., description="Average CP-SAT solver solve latency in milliseconds")
    mean_checker_ms: float = Field(..., description="Average independent checker validation latency in milliseconds")
    mean_peak_memory_mb: float = Field(..., description="Average peak memory usage in MB")
    budget_target_ms: float = Field(..., description="Engineering budget target in milliseconds")
    budget_compliant: bool = Field(..., description="Whether P50 satisfies declared engineering target")
    feasibility_rate_pct: float = Field(..., description="Percentage of runs achieving feasible solution")
    checker_pass_rate_pct: float = Field(..., description="Percentage of runs certified by oracle with 0 collisions")
    supported_status: str = Field(..., description="SUPPORTED_ENVELOPE, EXPLORATORY_BOUNDARY, or UNSUPPORTED")


class FailureScenarioResult(APIModel):
    """Result of an automated failure injection scenario."""
    scenario_id: str
    scenario_name: str
    injected_failure: str
    expected_behavior: str
    observed_outcome: str
    passed: bool
    latency_ms: float
    invariant_preserved: str


class SecurityAuditItem(APIModel):
    """Verification entry for security, sanitization, and isolation controls."""
    control_id: str
    control_category: str
    status: str
    description: str
    evidence_detail: str


class BackupRestoreDrillReport(APIModel):
    """Empirical backup and restoration drill metrics."""
    drill_id: str
    executed_at_utc: datetime
    records_backed_up: int
    backup_duration_ms: float
    restore_duration_ms: float
    rpo_seconds: float = Field(..., description="Recovery Point Objective achieved (seconds)")
    rto_seconds: float = Field(..., description="Recovery Time Objective achieved (seconds)")
    integrity_hash_matched: bool
    status: str
    offline_verified: bool


class ResilienceDashboardResponse(APIModel):
    """Comprehensive Phase 17 Resilience, Security, and Scaling Evidence Dashboard."""
    generated_at_utc: datetime
    hardware_tag: str
    overall_status: str
    benchmarks: List[WorkloadBenchmarkSummary]
    failure_scenarios: List[FailureScenarioResult]
    security_controls: List[SecurityAuditItem]
    backup_drill: BackupRestoreDrillReport
