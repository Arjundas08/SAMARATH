/**
 * Phase 14: Calculated Metrics, Fair Comparison & Stress Scenarios TypeScript Definitions.
 * Blueprint Sections: 26, 37-40.
 */

export type StressScenarioType =
  | 'WORK_DURATION_INCREASE'
  | 'LATE_RESOURCE_ARRIVAL'
  | 'SHIFTED_GOODS_FORECAST'
  | 'URGENT_UNPLANNED_WORK';

export interface OnTimeCoverageMetrics {
  total_tasks_in_scope: int;
  total_tasks_scheduled: int;
  total_tasks_unscheduled: int;
  overall_coverage_pct?: number | null;
  mandatory_tasks_total: int;
  mandatory_tasks_scheduled: int;
  mandatory_on_time_coverage_pct?: number | null;
  critical_tasks_total: int;
  critical_tasks_scheduled: int;
  critical_on_time_coverage_pct?: number | null;
  routine_tasks_total: int;
  routine_tasks_scheduled: int;
  permitted_lateness_count: int;
  permitted_lateness_total_minutes: int;
  unpermitted_lateness_count: int;
  unscheduled_by_reason: Record<string, int>;
}

type int = number;

export interface SegmentUnionOccupation {
  segment_id: string;
  segment_code: string;
  corridor_code: string;
  total_horizon_minutes: int;
  fixed_closure_minutes: int;
  maintenance_union_minutes: int;
  maintenance_sum_minutes: int;
  overlap_savings_minutes: int;
  net_available_minutes: int;
  utilization_pct?: number | null;
}

export interface InfrastructureOccupationMetrics {
  total_corridor_horizon_minutes: int;
  total_fixed_closures_minutes: int;
  total_maintenance_union_minutes: int;
  total_maintenance_sum_minutes: int;
  total_co_utilization_savings_minutes: int;
  network_utilization_pct?: number | null;
  segments: SegmentUnionOccupation[];
}

export interface QualityAndTimingMetrics {
  lock_preservation_pct?: number | null;
  hard_locks_total: int;
  hard_locks_preserved: int;
  hard_locks_violated: int;
  explanation_coverage_pct?: number | null;
  run_time_ms: number;
  model_generation_ms: number;
  solve_time_ms: number;
  checker_time_ms: number;
  variables_count: int;
  constraints_count: int;
  lattice_nodes_count: int;
}

export interface CalculatedPlanMetrics {
  metric_report_id: string;
  plan_id: string;
  plan_version: int;
  corridor_code: string;
  snapshot_id: string;
  calculator_version: string;
  rule_policy_version: string;
  domain_version: string;
  calculated_at: string;
  hardware_tag: string;
  coverage: OnTimeCoverageMetrics;
  occupation: InfrastructureOccupationMetrics;
  quality_and_timing: QualityAndTimingMetrics;
  scope_disclosure: string;
}

export interface FairComparisonResult {
  comparison_id: string;
  corridor_code: string;
  baseline_plan_id: string;
  candidate_plan_id: string;
  baseline_is_valid: boolean;
  candidate_is_valid: boolean;
  same_workload: boolean;
  same_horizon: boolean;
  same_resources: boolean;
  has_unequal_coverage: boolean;
  unequal_coverage_warning?: string | null;
  baseline_coverage_pct?: number | null;
  candidate_coverage_pct?: number | null;
  coverage_delta_pct?: number | null;
  mandatory_coverage_delta_pct?: number | null;
  baseline_union_occupation_minutes: int;
  candidate_union_occupation_minutes: int;
  occupation_savings_minutes: int;
  occupation_savings_pct?: number | null;
  baseline_metrics: CalculatedPlanMetrics;
  candidate_metrics: CalculatedPlanMetrics;
  summary_verdict: string;
  is_optimizer_underperforming: boolean;
  calculated_at: string;
}

export interface StressPerturbation {
  perturbation_id: string;
  scenario_type: StressScenarioType;
  target_entity_type: string;
  target_entity_id: string;
  magnitude_minutes: int;
  description: string;
}

export interface SingleScenarioResult {
  scenario_id: string;
  scenario_type: StressScenarioType;
  scenario_name: string;
  passed: boolean;
  first_violation_reason?: string | null;
  all_violation_reasons: string[];
  worst_excess_minutes: int;
  mandatory_tasks_affected: int;
  is_rule_change_invalidation: boolean;
}

export interface FixedPlanStressReport {
  stress_test_id: string;
  plan_id: string;
  corridor_code: string;
  total_scenarios_tested: int;
  passed_scenarios_count: int;
  failed_scenarios_count: int;
  pass_display: string;
  scenarios: SingleScenarioResult[];
  tested_at: string;
  hardware_tag: string;
  scope_disclosure: string;
}

export interface AdaptiveStressRecoveryResult {
  experiment_id: string;
  baseline_plan_id: string;
  scenario_type: StressScenarioType;
  perturbation_description: string;
  fixed_plan_survived: boolean;
  replan_attempted: boolean;
  replan_succeeded: boolean;
  replan_runtime_ms: number;
  replan_plan_id?: string | null;
  replan_churn_score?: number | null;
  recovered_mandatory_coverage_pct?: number | null;
  summary: string;
}
