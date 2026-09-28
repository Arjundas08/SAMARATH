/**
 * Phase 17 – Failure Recovery, Security & Scaling Evidence Types.
 * Matches backend app.schemas.resilience.
 */

export interface BenchmarkStageMetrics {
  candidate_gen_ms: number;
  model_construction_ms: number;
  solve_time_ms: number;
  checker_verify_ms: number;
  total_roundtrip_ms: number;
  peak_memory_mb: number;
  scheduled_tasks: number;
  total_tasks: number;
  checker_passed: boolean;
}

export interface WorkloadBenchmarkSummary {
  workload_tasks: number;
  sample_count: number;
  seeds_tested: number[];
  p50_total_ms: number;
  p95_total_ms: number;
  mean_solve_ms: number;
  mean_checker_ms: number;
  mean_peak_memory_mb: number;
  budget_target_ms: number;
  budget_compliant: boolean;
  feasibility_rate_pct: number;
  checker_pass_rate_pct: number;
  supported_status: 'SUPPORTED_ENVELOPE' | 'EXPLORATORY_BOUNDARY' | 'UNSUPPORTED' | string;
}

export interface FailureScenarioResult {
  scenario_id: string;
  scenario_name: string;
  injected_failure: string;
  expected_behavior: string;
  observed_outcome: string;
  passed: boolean;
  latency_ms: number;
  invariant_preserved: string;
}

export interface SecurityAuditItem {
  control_id: string;
  control_category: string;
  status: 'VERIFIED' | 'FAILED' | string;
  description: string;
  evidence_detail: string;
}

export interface BackupRestoreDrillReport {
  drill_id: string;
  executed_at_utc: string;
  records_backed_up: number;
  backup_duration_ms: number;
  restore_duration_ms: number;
  rpo_seconds: number;
  rto_seconds: number;
  integrity_hash_matched: boolean;
  status: string;
  offline_verified: boolean;
}

export interface ResilienceDashboardResponse {
  generated_at_utc: string;
  hardware_tag: string;
  overall_status: string;
  benchmarks: WorkloadBenchmarkSummary[];
  failure_scenarios: FailureScenarioResult[];
  security_controls: SecurityAuditItem[];
  backup_drill: BackupRestoreDrillReport;
}
