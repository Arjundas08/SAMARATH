/**
 * Phase 16 – Execution Feedback, Partial Work, and Estimate Review Types.
 */

export type ExecutionStatus = 'COMPLETED' | 'PARTIAL' | 'ABANDONED' | 'CANCELLED_EXTERNALLY';

export type ChronologyValidationStatus = 'VALID' | 'INVALID_CHRONOLOGY' | 'MISSING_RELEASE' | 'UNRESOLVED_CONFLICT';

export type DeviationReason =
  | 'NONE'
  | 'MACHINE_BREAKDOWN'
  | 'WEATHER_ADVERSE'
  | 'LATE_POSSESSION_HANDOVER'
  | 'EARLY_BURST_CANCEL'
  | 'UNEXPECTED_SITE_CONDITION'
  | 'OTHER';

export type EstimateReviewRecommendation =
  | 'MAINTAIN_CURRENT'
  | 'INCREASE_BUFFER'
  | 'DECREASE_BUFFER'
  | 'SPLIT_WORK_PACKAGE';

export interface ExecutionRecordCreate {
  task_id: string;
  plan_id?: string;
  assignment_id?: string;
  external_authority_ref?: string;
  actual_start_utc: string;
  actual_restoration_utc: string;
  actual_release_utc?: string;
  quantity_completed: number;
  quantity_units: string;
  target_quantity?: number;
  planned_duration_minutes?: number;
  resource_use?: Array<{ resource_id: string; hours: number }>;
  still_occupied_resources?: string[];
  deviation_reason?: DeviationReason;
  deviation_notes?: string;
  provenance_mode?: string;
  idempotency_key?: string;
}

export interface ExecutionRecord {
  record_id: string;
  revision: number;
  superseded_by_record_id?: string;
  is_latest_revision: boolean;
  task_id: string;
  plan_id?: string;
  assignment_id?: string;
  external_authority_ref?: string;
  actual_start_utc: string;
  actual_restoration_utc: string;
  actual_release_utc?: string;
  quantity_completed: number;
  quantity_units: string;
  target_quantity?: number;
  execution_status: ExecutionStatus;
  planned_duration_minutes?: number;
  actual_duration_minutes?: number;
  overrun_minutes?: number;
  quantity_variance?: number;
  resource_use: Array<{ resource_id: string; hours: number }>;
  still_occupied_resources: string[];
  deviation_reason: DeviationReason;
  deviation_notes?: string;
  chronology_status: ChronologyValidationStatus;
  has_missing_release: boolean;
  missing_attribution_explanation?: string;
  provenance_mode: string;
  created_at_utc: string;
  recorded_by_user_id: string;
  content_hash: string;
}

export interface ResidualWorkConfirmRequest {
  source_record_id: string;
  confirmed_residual_quantity: number;
  quantity_units: string;
  site_state: string;
  dependencies?: string[];
  applicable_deadline_utc?: string;
  priority?: string;
}

export interface ResidualWorkTask {
  residual_task_id: string;
  original_task_id: string;
  source_record_id: string;
  completed_quantity: number;
  residual_quantity: number;
  total_target_quantity: number;
  quantity_units: string;
  site_state: string;
  dependencies: string[];
  applicable_deadline_utc?: string;
  priority: string;
  is_confirmed: boolean;
  confirmed_by_user_id: string;
  created_at_utc: string;
}

export interface PlanVsActualVariance {
  task_id: string;
  plan_id?: string;
  planned_start_utc?: string;
  actual_start_utc?: string;
  start_delay_minutes?: number;
  planned_duration_minutes?: number;
  actual_duration_minutes?: number;
  duration_overrun_minutes?: number;
  planned_quantity?: number;
  actual_quantity: number;
  quantity_units: string;
  quantity_completion_pct?: number;
  status: ExecutionStatus;
  attribution_notes: string;
}

export interface ReconciliationQueueItem {
  conflict_id: string;
  task_id: string;
  conflict_type: string;
  source_a: string;
  source_b?: string;
  description: string;
  severity: string;
  is_resolved: boolean;
  resolution_notes?: string;
  created_at_utc: string;
}

export interface EstimateReviewSummary {
  task_category: string;
  department: string;
  sample_size: number;
  mean_planned_minutes: number;
  mean_actual_minutes: number;
  mean_overrun_pct: number;
  recommended_action: EstimateReviewRecommendation;
  suggested_buffer_minutes: number;
  review_notes: string;
  requires_policy_revision: boolean;
}

export interface EstimateReviewResponse {
  summaries: EstimateReviewSummary[];
  total_records_analyzed: number;
  generated_at_utc: string;
}
