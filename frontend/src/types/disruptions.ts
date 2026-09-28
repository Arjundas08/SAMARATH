/**
 * Phase 13: Disruption Events, Stable Replanning & PlanDiff TypeScript Definitions.
 * Blueprint Sections: 27-28, 34 plus addendum.
 */

export type DisruptionEventType =
  | 'TASK_CRITICALITY_CHANGE'
  | 'TASK_DEADLINE_CHANGE'
  | 'TASK_DURATION_CHANGE'
  | 'TRAIN_OCCUPATION_CHANGE'
  | 'TRAIN_FORECAST_UPDATE'
  | 'RESOURCE_AVAILABILITY_CHANGE'
  | 'RESOURCE_OUTAGE'
  | 'WINDOW_CHANGE'
  | 'WINDOW_REVOCATION'
  | 'RULE_CHANGE'
  | 'TOPOLOGY_CHANGE'
  | 'LOCK_IMPOSED'
  | 'LOCK_RELEASED'
  | 'REJECTION_ISSUED'
  | 'EXECUTION_OBSERVATION'
  | 'TASK_ADDED'
  | 'TASK_WITHDRAWN';

export type EventSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type ProcessingStatus =
  | 'RECEIVED'
  | 'VALIDATED'
  | 'COALESCED'
  | 'PROCESSING'
  | 'COMPLETED'
  | 'SUPERSEDED'
  | 'FAILED';

export type DiffCategory =
  | 'UNCHANGED'
  | 'SHIFTED'
  | 'RESOURCE_CHANGED'
  | 'REPACKAGED'
  | 'ADDED'
  | 'CANCELLED'
  | 'NOW_UNSCHEDULED'
  | 'COMPLETED';

export interface DisruptionPayload {
  entity_type: string;
  entity_id: string;
  field_changed?: string;
  old_value?: any;
  new_value?: any;
  affected_track_segments?: string[];
  effective_start_utc?: string;
  effective_end_utc?: string;
  metadata?: Record<string, any>;
}

export interface DisruptionEvent {
  event_id: string;
  event_type: DisruptionEventType;
  severity: EventSeverity;
  corridor_code: string;
  source_system: string;
  source_order: number;
  idempotency_key: string;
  payload: DisruptionPayload;
  description: string;
  submitted_by: string;
  created_at: string;
  processing_status: ProcessingStatus;
  affected_plan_ids: string[];
}

export interface DisruptionEventCreate {
  event_type: DisruptionEventType;
  severity?: EventSeverity;
  corridor_code: string;
  source_system: string;
  source_order: number;
  idempotency_key: string;
  payload: DisruptionPayload;
  description: string;
  submitted_by?: string;
}

export interface PlanDiffEntry {
  assignment_id: string;
  task_id: string;
  task_name?: string;
  task_type?: string;
  category: DiffCategory;
  from_start_time?: string;
  to_start_time?: string;
  from_end_time?: string;
  to_end_time?: string;
  from_resource_ids: string[];
  to_resource_ids: string[];
  from_track_segment_ids: string[];
  to_track_segment_ids: string[];
  start_shift_minutes: number;
  duration_shift_minutes: number;
  displacement_minutes: number;
  resource_changed: boolean;
  track_changed: boolean;
  is_hard_locked: boolean;
  lock_type?: string;
  rejection_reason?: string;
}

export interface PlanDiffSummary {
  diff_id: string;
  from_plan_id: string;
  to_plan_id: string;
  corridor_code: string;
  from_plan_version?: number;
  to_plan_version?: number;
  unchanged_count: number;
  shifted_count: number;
  resource_changed_count: number;
  repackaged_count: number;
  added_count: number;
  cancelled_count: number;
  now_unscheduled_count: number;
  completed_count: number;
  total_comparable: number;
  total_changes: number;
  churn_score: number;
  stability_ratio: number;
  displaced_minutes_total: number;
  displaced_minutes_max: number;
  displaced_minutes_avg: number;
  scope_disclosure: string;
  diff_reason?: string;
  created_at: string;
}

export interface PlanDiffResponse {
  summary: PlanDiffSummary;
  entries: PlanDiffEntry[];
}

export interface ImpactClosureItem {
  entity_type: string;
  entity_id: string;
  impact_type: string;
  reason: string;
  is_locked: boolean;
  affected_plans: string[];
}

export interface ImpactClosureResponse {
  event_ids: string[];
  total_affected_items: number;
  items: ImpactClosureItem[];
  scope_disclosure: string;
}

export interface StableReplanRequest {
  corridor_code: string;
  event_ids?: string[];
  coalesce_pending?: boolean;
  baseline_plan_id?: string;
  time_limit_seconds?: number;
  preserve_locks?: boolean;
}

export interface StableReplanResponse {
  replan_job_id?: string;
  status: string;
  message: string;
  event_ids_processed: string[];
  baseline_plan_id?: string;
  lock_conflicts?: Array<{
    task_id: string;
    lock_type: string;
    conflict_reason: string;
  }>;
  created_at: string;
}

export interface LockEscalationConflict {
  task_id: string;
  lock_type: string;
  reason: string;
}

export interface EscalationCheckResponse {
  plan_id: string;
  has_conflicts: boolean;
  escalation_count: number;
  escalations: LockEscalationConflict[];
  recommendation: string;
}
