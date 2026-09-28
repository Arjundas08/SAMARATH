/**
 * TypeScript API Contracts and Entity Definitions for SAMARATH.
 * Generated from backend Pydantic schemas.
 */

export type DepartmentType = 'ENGINEERING' | 'SIGNALLING' | 'ELECTRICAL';
export type CriticalityTier = 'TIER_1_MANDATORY' | 'TIER_2_SPEED_RESTRICTION' | 'TIER_3_CYCLIC';
export type DemandStatus = 'DRAFT' | 'SUBMITTED' | 'VALIDATED' | 'WITHDRAWN' | 'SUPERSEDED';
export type ProvenanceMode = 'TEST' | 'SYNTHETIC_SCENARIO' | 'AUTHORIZED_IMPORT';
export type ObjectiveProfile = 'PROGRAMME_IMPROVEMENT' | 'DISRUPTION_RECOVERY';
export type JobState = 'QUEUED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
export type SolverStatus = 'OPTIMAL' | 'FEASIBLE' | 'INFEASIBLE' | 'TIME_LIMIT' | 'NOT_SOLVED';
export type StopReason = 'OPTIMAL_PROVEN' | 'TIME_LIMIT_REACHED' | 'INFEASIBILITY_PROVEN' | 'USER_CANCELLED' | 'ERROR';
export type ValidationVerdict = 'VERIFIED_FEASIBLE' | 'VERIFICATION_FAILED' | 'UNKNOWN_BLOCKED';
export type RuleVerdict = 'PASS' | 'FAIL' | 'UNKNOWN';
export type PlanStatus = 'DRAFT_PROPOSAL' | 'CHECKED_FEASIBLE' | 'JOINT_REVIEW' | 'APPROVED_PROGRAMME' | 'STALE';
export type ProgrammeAuthorityState = 'PROPOSED' | 'RECOMMENDED' | 'OPERATING_RATIFIED';
export type FieldAuthorityState = 'NOT_REQUESTED' | 'EXTERNAL_PERMIT_PENDING' | 'EXTERNAL_PERMIT_GRANTED' | 'WORK_IN_PROGRESS' | 'CLEARED';
export type ApprovalEligibility = 'ELIGIBLE' | 'BLOCKED_CHECK_FAILED' | 'BLOCKED_UNKNOWN_RULE' | 'BLOCKED_LOCKED_CONFLICT' | 'BLOCKED_STALE_INPUT';
export type ResourceType = 'MACHINE' | 'CREW' | 'SPECIAL_EQUIPMENT';
export type TrackDirection = 'UP' | 'DOWN' | 'BOTH';

export type UserRole =
  | 'DEPARTMENT_PLANNER'
  | 'CORRIDOR_COORDINATOR'
  | 'OPERATING_REVIEWER'
  | 'DELEGATED_APPROVER'
  | 'INTEGRATION_OPERATOR'
  | 'RULE_AUTHOR'
  | 'RULE_APPROVER'
  | 'AUDITOR'
  | 'INFRASTRUCTURE_ADMIN';

export type Permission =
  | 'DEMAND_READ'
  | 'DEMAND_CREATE'
  | 'DEMAND_MUTATE'
  | 'TIMETABLE_READ'
  | 'TIMETABLE_MUTATE'
  | 'SOLVE_TRIGGER'
  | 'PROGRAMME_REVIEW'
  | 'PROGRAMME_APPROVE'
  | 'RULE_EDIT'
  | 'RULE_APPROVE'
  | 'AUDIT_READ'
  | 'SYSTEM_ADMIN';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface SessionResponse {
  user_id: string;
  username: string;
  display_name: string;
  roles: UserRole[];
  permissions: Permission[];
  department?: string | null;
  territory: string;
  csrf_token: string;
  is_authenticated: boolean;
}

export interface DatabaseHealth {
  connected: boolean;
  engine: string;
  latency_ms?: number | null;
  error?: string | null;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  app_name: string;
  version: string;
  process: string;
  database: DatabaseHealth;
  timestamp_utc: string;
}

export interface PreferredWindow {
  window_start_utc: string;
  window_end_utc: string;
}

export interface ResourceRequirement {
  resource_type: ResourceType;
  resource_id: string;
  quantity: number;
}

export interface Task {
  task_id: string;
  business_key: string;
  department: DepartmentType;
  sub_department: string;
  work_type: string;
  description: string;
  station_from: string;
  station_to: string;
  track_segment_id: string;
  chainage_start_km: number;
  chainage_end_km: number;
  duration_minutes: number;
  setup_buffer_minutes: number;
  restoration_buffer_minutes: number;
  total_block_minutes: number;
  criticality: CriticalityTier;
  deadline_utc: string;
  preferred_windows: PreferredWindow[];
  required_resources: ResourceRequirement[];
  requires_power_block: boolean;
  power_block_elementary_section?: string | null;
  requires_speed_restriction_after: boolean;
  imposed_speed_kmh?: number | null;
  demand_status: DemandStatus;
  provenance_mode: ProvenanceMode;
  created_at_utc: string;
  created_by: string;
}

export interface TrainOccupation {
  occupation_id: string;
  train_number: string;
  train_type: string;
  track_segment_id: string;
  entry_time_utc: string;
  exit_time_utc: string;
  start_minute: number;
  end_minute: number;
}

export interface ResourceCalendarEntry {
  entry_id: string;
  resource_id: string;
  resource_type: string;
  available_start_utc: string;
  available_end_utc: string;
  is_outage: boolean;
  outage_reason?: string | null;
}

export interface LockedCommitment {
  commitment_id: string;
  task_id: string;
  track_segment_id: string;
  start_utc: string;
  end_utc: string;
  locked_by: string;
  lock_reason: string;
}

export interface Snapshot {
  snapshot_id: string;
  corridor_code: string;
  horizon_start_utc: string;
  horizon_end_utc: string;
  provenance_mode: ProvenanceMode;
  tasks: Task[];
  train_occupations: TrainOccupation[];
  resource_calendars: ResourceCalendarEntry[];
  locked_commitments: LockedCommitment[];
  snapshot_hash: string;
  is_sealed: boolean;
  created_at_utc: string;
  created_by: string;
}

export interface WorkPhaseSchedule {
  setup_start_utc: string;
  setup_end_utc: string;
  work_start_utc: string;
  work_end_utc: string;
  restoration_start_utc: string;
  restoration_end_utc: string;
}

export interface CheckerPhaseItem {
  phase_name: string;
  start_utc: string;
  end_utc: string;
  required_resources?: ResourceRequirement[];
}

export type WorkPhaseScheduleType = CheckerPhaseItem[] | WorkPhaseSchedule | any[];

export interface MaterializedAssignment {
  assignment_id: string;
  plan_id: string;
  task_id: string;
  business_key: string;
  track_segment_id: string;
  start_utc: string;
  end_utc: string;
  start_minute: number;
  end_minute: number;
  duration_minutes: number;
  work_phase_schedule: WorkPhaseScheduleType;
  assigned_resources: ResourceRequirement[];
  power_block_required: boolean;
  power_block_section?: string | null;
  is_locked: boolean;
  is_shadow_block: boolean;
  bundled_with_task_ids: string[];
}

export interface PlanMetric {
  total_tasks_demanded?: number;
  total_tasks_scheduled?: number;
  statutory_safety_compliance_pct?: number;
  corridor_availability_hours?: number;
  total_possession_hours?: number;
  multi_dept_shadow_blocks_count?: number;
  estimated_train_impact_index?: number;
  unscheduled_mandatory_count?: number;
  [key: string]: any;
}

export interface PlanVersion {
  plan_id: string;
  plan_version_number: number;
  corridor_code?: string;
  snapshot_id: string;
  parent_plan_id?: string | null;
  validation_id?: string | null;
  horizon_type: 'MONTHLY' | 'WEEKLY' | string;
  plan_status: PlanStatus | string;
  solver_status?: string | null;
  checker_verdict?: string | null;
  programme_authority_state: ProgrammeAuthorityState | string;
  field_authority_state: FieldAuthorityState | string;
  approval_eligibility: ApprovalEligibility | string;
  metrics: PlanMetric;
  assignments: MaterializedAssignment[];
  reconciliation_cases?: any[];
  created_at_utc: string;
  approved_at_utc?: string | null;
  approved_by_officer?: string | null;
}

export interface StationInfo {
  station_code: string;
  station_name: string;
  chainage_km: number;
  absolute_distance_meters: number;
  total_lines: number;
  has_crossover: boolean;
}

export interface TrackSegmentInfo {
  segment_id: string;
  station_from: string;
  station_to: string;
  direction: 'UP' | 'DOWN' | 'BOTH';
  chainage_start_km: number;
  chainage_end_km: number;
  length_meters: number;
  max_permissible_speed_kmh: number;
  elementary_section_id: string;
}

export interface CorridorTopology {
  corridor_code: string;
  corridor_name: string;
  total_length_km: number;
  stations: StationInfo[];
  track_segments: TrackSegmentInfo[];
}

export interface MonthlyTaskAllocation {
  task_id: string;
  business_key: string;
  department: string;
  track_segment_id: string;
  duration_minutes: number;
  allocated_week: number;
  allocation_status: string;
  allocation_reason: string;
  is_hard_lock: boolean;
  required_resources: ResourceRequirement[];
}

export interface WeeklyQuotaBudget {
  week_index: number;
  max_possession_minutes: number;
  allocated_possession_minutes: number;
  machine_quotas: Record<string, number>;
  allocated_machine_days: Record<string, number>;
}

export interface MonthlyAllocationPlan {
  monthly_plan_id: string;
  corridor_code: string;
  version_number: number;
  status: string;
  planning_month: string;
  quota_budgets: WeeklyQuotaBudget[];
  allocations: MonthlyTaskAllocation[];
  unallocated_task_ids: string[];
  department_breakdown: Record<string, number>;
  created_at_utc: string;
}

export interface ReconciliationCase {
  case_id: string;
  parent_monthly_plan_id: string;
  child_weekly_plan_id: string;
  task_id: string;
  business_key: string;
  variance_type: string;
  allocated_week: number;
  scheduled_week: number;
  variance_description: string;
  status: string;
  impact_summary: Record<string, any>;
  created_at_utc: string;
}

export type JobPhase =
  | 'QUEUED'
  | 'CLAIMED'
  | 'PREPARING_SNAPSHOT'
  | 'BUILDING_CANDIDATES'
  | 'SOLVING'
  | 'VERIFYING_FEASIBILITY'
  | 'RECONCILING'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED';

export interface SolveJobCreateRequest {
  corridor_code: string;
  snapshot_id?: string | null;
  profile?: ObjectiveProfile;
  time_limit_seconds?: number;
  num_workers?: number;
  random_seed?: number;
  lattice_step_minutes?: number;
  max_candidates?: number;
  parent_monthly_plan_id?: string | null;
  target_week_index?: number | null;
}

export interface SolveJobResponse {
  job_id: string;
  corridor_code: string;
  snapshot_id: string;
  objective_profile: ObjectiveProfile;
  status: JobState;
  current_phase: JobPhase | string;
  progress_percentage: number;
  attempt_count: number;
  version: number;
  fencing_token: number;
  lease_owner?: string | null;
  lease_expires_at?: string | null;
  created_at_utc: string;
  completed_at_utc?: string | null;
  status_url: string;
  etag: string;
  result_plan_id?: string | null;
  error_detail?: string | null;
  is_snapshot_obsolete: boolean;
  result_summary?: Record<string, any> | null;
}

export interface SolveJobListResponse {
  jobs: SolveJobResponse[];
  total: number;
}

// ==========================================
// Phase 12: Why & Why-Not Diagnostics Types
// ==========================================

export type DiagnosticReasonCode =
  | 'INPUT_BLOCKED'
  | 'CANDIDATE_REJECTED'
  | 'NO_CANDIDATE_IN_DOMAIN'
  | 'MODEL_INFEASIBLE'
  | 'FEASIBLE_BUT_UNSELECTED'
  | 'SEARCH_INCOMPLETE';

export type ProofStatus =
  | 'PROVEN_CONSTRAINED'
  | 'PROVEN_SUBOPTIMAL'
  | 'EMPIRICALLY_CONFLICTING'
  | 'INCONCLUSIVE';

export type RepairActionType =
  | 'MOVE_OPTIONAL_UNLOCKED_WORK'
  | 'SUBSTITUTE_RESOURCE'
  | 'ALTERNATE_PACKAGE_WINDOW'
  | 'REQUEST_PARENT_WEEK_AMENDMENT';

export type RepairFeasibilityStatus =
  | 'VERIFIED_FEASIBLE'
  | 'AWAITING_AUTHORITY'
  | 'INVALID';

export interface DiagnosticEvidenceFact {
  fact_key: string;
  fact_label: string;
  required_value: any;
  observed_value: any;
  source_record_id: string;
  rule_version?: string;
  is_satisfied: boolean;
}

export interface ConflictCore {
  conflicting_train_numbers?: string[];
  conflicting_assignment_ids?: string[];
  exhausted_resources?: string[];
  violated_rules?: string[];
  temporal_interval_minutes?: [number, number];
}

export interface CounterfactualComparison {
  alternative_window_id: string;
  alternative_start_minute: number;
  alternative_end_minute: number;
  objective_value_delta: number;
  comparison_outcome: string;
  explanation: string;
}

export interface RepairOption {
  action_type: RepairActionType;
  description: string;
  required_role: string;
  affected_records?: string[];
  feasibility_status?: RepairFeasibilityStatus;
  estimated_gain_minutes?: number;
  proposed_value?: string;
}

export interface WhyNotDiagnostic {
  task_id: string;
  task_business_key: string;
  plan_id: string;
  snapshot_id: string;
  reason_code: DiagnosticReasonCode;
  proof_status: ProofStatus;
  primary_cause_summary: string;
  explanation_narrative: string;
  facts: DiagnosticEvidenceFact[];
  conflict_core: ConflictCore;
  permitted_repairs: RepairOption[];
  evaluated_at_utc?: string;
  solver_time_budget_seconds?: number;
}

export interface WhySelectedDiagnostic {
  assignment_id: string;
  task_id: string;
  task_business_key: string;
  plan_id: string;
  start_minute: number;
  end_minute: number;
  track_segment_id: string;
  objective_contributions: Record<string, number>;
  admissibility_facts: DiagnosticEvidenceFact[];
  counterfactual_comparisons: CounterfactualComparison[];
  evaluated_at_utc?: string;
}

export interface TrialRepairRequest {
  plan_id: string;
  task_id: string;
  repair_id: string;
  action_type: RepairActionType;
  proposed_value: string;
}

export interface TrialRepairResult {
  repair_id: string;
  is_publishable: boolean;
  checker_verdict: string;
  objective_before: number;
  objective_after: number;
  objective_improvement: number;
  placed_task_ids: string[];
  remaining_conflicts: string[];
  runtime_ms: number;
  simulated_assignments_count: number;
}

export interface ApplyRepairRequest {
  plan_id: string;
  task_id: string;
  repair_id: string;
  expected_plan_version: number;
  authorized_by_role: string;
  justification: string;
}

export interface ApplyRepairResponse {
  applied_repair_id: string;
  new_snapshot_id: string;
  new_job_id: string;
  status: string;
  message: string;
}

