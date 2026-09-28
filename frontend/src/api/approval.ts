/**
 * Phase 15: Human Review, Programme Approval, and Audit Integrity API Client.
 */
import {
  PlanLock,
  ReviewDecision,
  ApprovalResult,
  ApprovalEligibility,
  AuditTrailResponse,
  EvidenceExport,
  PlanApprovalSummary,
  ReviewAction,
  ApprovalAction,
  LockCategory,
} from '../types/approval';

const API_BASE = '/api/v1/approval';

export class ApprovalApi {
  /**
   * Register a plan for approval workflow.
   */
  static async registerPlan(payload: {
    plan_id?: string;
    plan_data: any;
    provenance_mode?: string;
  }): Promise<{ plan_id: string; content_hash: string; etag: string; version_epoch: number }> {
    const response = await fetch(`${API_BASE}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Plan registration failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Submit plan for joint review.
   */
  static async submitForReview(payload: {
    plan_id: string;
    plan_version: number;
    plan_content_hash: string;
    comment?: string;
  }): Promise<{ plan_id: string; new_status: string; version_epoch: number; etag: string }> {
    const response = await fetch(`${API_BASE}/submit-review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Submit for review failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Submit a review decision (RECOMMEND, REQUEST_REVISION, REJECT).
   */
  static async submitReview(payload: {
    plan_id: string;
    plan_version: number;
    plan_content_hash: string;
    checker_result_id?: string;
    action: ReviewAction;
    comment?: string;
    reviewed_assignments?: string[];
  }): Promise<ReviewDecision> {
    const response = await fetch(`${API_BASE}/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Review submission failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Pre-flight approval eligibility check.
   */
  static async checkEligibility(planId: string): Promise<ApprovalEligibility> {
    const response = await fetch(`${API_BASE}/eligibility/${encodeURIComponent(planId)}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Eligibility check failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Atomic approval transaction.
   */
  static async processApproval(payload: {
    plan_id: string;
    plan_version: number;
    plan_content_hash: string;
    expected_version_epoch: number;
    expected_etag: string;
    action: ApprovalAction;
    comment?: string;
    idempotency_key: string;
  }): Promise<ApprovalResult> {
    const response = await fetch(`${API_BASE}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok && response.status !== 409) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Approval processing failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Create a field-level lock on an assignment.
   */
  static async createLock(payload: {
    plan_id: string;
    assignment_id: string;
    lock_category: LockCategory;
    reason: string;
  }): Promise<PlanLock> {
    const response = await fetch(`${API_BASE}/lock`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Lock creation failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Revise an existing lock.
   */
  static async reviseLock(payload: {
    lock_id: string;
    new_category?: LockCategory;
    new_reason: string;
  }): Promise<PlanLock> {
    const response = await fetch(`${API_BASE}/lock/revise`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Lock revision failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get all active locks for a plan.
   */
  static async getLocks(planId: string): Promise<PlanLock[]> {
    const response = await fetch(`${API_BASE}/locks/${encodeURIComponent(planId)}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Get locks failed: ${response.status}`);
    }
    const data = await response.json();
    return data.locks || [];
  }

  /**
   * Query append-only audit trail.
   */
  static async queryAuditTrail(scope?: string, limit: number = 50): Promise<AuditTrailResponse> {
    const params = new URLSearchParams();
    if (scope) params.append('scope', scope);
    params.append('limit', String(limit));

    const response = await fetch(`${API_BASE}/audit?${params.toString()}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Audit query failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Export evidence with provenance manifest.
   */
  static async exportEvidence(planId: string): Promise<EvidenceExport> {
    const response = await fetch(`${API_BASE}/export/${encodeURIComponent(planId)}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Evidence export failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Get plan approval summary.
   */
  static async getPlanSummary(planId: string): Promise<PlanApprovalSummary> {
    const response = await fetch(`${API_BASE}/summary/${encodeURIComponent(planId)}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Get plan summary failed: ${response.status}`);
    }
    return response.json();
  }
}
