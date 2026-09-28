/**
 * Phase 15 – Approval Workflow TypeScript types.
 */

export type ReviewAction = 'RECOMMEND' | 'REQUEST_REVISION' | 'REJECT';
export type ApprovalAction = 'APPROVE' | 'REJECT';
export type LockCategory = 'SCHEDULE_WINDOW' | 'RESOURCE_ASSIGNMENT' | 'TRACK_ALLOCATION' | 'DURATION_ESTIMATE' | 'PRIORITY_OVERRIDE';
export type LockAuthority = 'PLANNER' | 'COORDINATOR' | 'OPERATING_REVIEWER' | 'APPROVER';

export type AuditEventType =
  | 'PLAN_SUBMITTED_FOR_REVIEW'
  | 'REVIEW_DECISION'
  | 'LOCK_CREATED'
  | 'LOCK_REVISED'
  | 'APPROVAL_ATTEMPTED'
  | 'APPROVAL_GRANTED'
  | 'APPROVAL_REJECTED'
  | 'STALENESS_DETECTED'
  | 'EVIDENCE_EXPORTED'
  | 'IDEMPOTENT_DUPLICATE';

export type ApprovalBlockReason =
  | 'CHECKER_NOT_VALID'
  | 'PLAN_HASH_MISMATCH'
  | 'VERSION_EPOCH_STALE'
  | 'ETAG_MISMATCH'
  | 'MISSING_REVIEW_RECOMMENDATION'
  | 'ROLE_INSUFFICIENT'
  | 'ADMIN_CANNOT_APPROVE'
  | 'SELF_APPROVAL_PROHIBITED'
  | 'RECONCILIATION_REQUIRED'
  | 'MISSING_MANDATORY_EVIDENCE'
  | 'CONCURRENT_MUTATION_DETECTED'
  | 'LOCKED_CONFLICT';

export interface PlanLock {
  lock_id: string;
  plan_id: string;
  assignment_id: string;
  lock_category: LockCategory;
  lock_authority: LockAuthority;
  locked_by_user_id: string;
  locked_by_display_name: string;
  locked_at_utc: string;
  revision: number;
  reason: string;
  is_active: boolean;
}

export interface ReviewDecision {
  decision_id: string;
  plan_id: string;
  plan_version: number;
  plan_content_hash: string;
  reviewer_user_id: string;
  reviewer_display_name: string;
  reviewer_role: string;
  action: ReviewAction;
  comment: string;
  reviewed_assignments: string[];
  decided_at_utc: string;
  correlation_id: string;
}

export interface ApprovalBlockDetail {
  reason: ApprovalBlockReason;
  description: string;
  navigation_target?: string;
}

export interface ApprovalResult {
  success: boolean;
  plan_id: string;
  plan_version: number;
  action?: ApprovalAction;
  new_plan_status?: string;
  new_authority_state?: string;
  approved_at_utc?: string;
  approved_by?: string;
  block_reasons: ApprovalBlockDetail[];
  audit_event_id?: string;
  was_idempotent_duplicate: boolean;
}

export interface ApprovalEligibility {
  plan_id: string;
  is_eligible: boolean;
  block_reasons: ApprovalBlockDetail[];
  current_plan_hash: string;
  current_version_epoch: number;
  current_etag: string;
  has_valid_checker_result: boolean;
  has_review_recommendation: boolean;
  pending_reconciliation: boolean;
}

export interface AuditEvent {
  event_id: string;
  event_type: AuditEventType;
  actor_user_id: string;
  actor_display_name: string;
  actor_role: string;
  scope: string;
  timestamp_utc: string;
  reason: string;
  before_ref?: string;
  after_ref?: string;
  content_hash: string;
  correlation_id: string;
  previous_event_hash: string;
  chain_sequence: number;
}

export interface AuditTrailResponse {
  events: AuditEvent[];
  total_count: number;
  chain_head_hash: string;
  chain_integrity_verified: boolean;
}

export interface EvidenceManifestEntry {
  source_type: string;
  source_id: string;
  source_version?: number;
  content_hash: string;
  status: string;
}

export interface EvidenceExport {
  export_id: string;
  plan_id: string;
  plan_version: number;
  exported_at_utc: string;
  exported_by_user_id: string;
  exported_by_display_name: string;
  plan_status: string;
  programme_authority_state: string;
  provenance_mode: string;
  disclaimer: string;
  manifest: EvidenceManifestEntry[];
  audit_trail_summary: AuditEvent[];
  content_hash: string;
}

export interface PlanApprovalSummary {
  plan_id: string;
  plan_status: string;
  programme_authority_state: string;
  content_hash: string;
  etag: string;
  version_epoch: number;
  review_count: number;
  has_recommendation: boolean;
  active_locks: number;
  checker_valid: boolean;
  provenance_mode: string;
}
