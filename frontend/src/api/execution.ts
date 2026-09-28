/**
 * Phase 16 – Execution Feedback, Partial Work, and Estimate Review API Client.
 */
import {
  ExecutionRecord,
  ResidualWorkConfirmRequest,
  ResidualWorkTask,
  PlanVsActualVariance,
  ReconciliationQueueItem,
  EstimateReviewResponse,
  DeviationReason,
} from '../types/execution';

const API_BASE = '/api/v1/execution';

export class ExecutionApi {
  /**
   * Ingest an authoritative or TEST execution observation.
   */
  static async recordExecution(payload: {
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
  }): Promise<ExecutionRecord> {
    const response = await fetch(`${API_BASE}/record`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Execution record intake failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Audited correction superseding old record and invalidating affected plans.
   */
  static async reviseExecution(payload: {
    record_id: string;
    correction_reason: string;
    actual_start_utc?: string;
    actual_restoration_utc?: string;
    actual_release_utc?: string;
    quantity_completed?: number;
    quantity_units?: string;
    deviation_reason?: DeviationReason;
    deviation_notes?: string;
  }): Promise<ExecutionRecord> {
    const response = await fetch(`${API_BASE}/revise`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Execution revision failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Confirm governed residual work without double counting.
   */
  static async confirmResidualWork(payload: ResidualWorkConfirmRequest): Promise<ResidualWorkTask> {
    const response = await fetch(`${API_BASE}/residual/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Residual confirmation failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * List latest execution records.
   */
  static async listRecords(taskId?: string): Promise<ExecutionRecord[]> {
    const query = taskId ? `?task_id=${encodeURIComponent(taskId)}` : '';
    const response = await fetch(`${API_BASE}/records${query}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `List records failed: ${response.status}`);
    }
    const data = await response.json();
    return data.records || [];
  }

  /**
   * Get plan-vs-actual variance for a task.
   */
  static async getVariance(taskId: string): Promise<PlanVsActualVariance> {
    const response = await fetch(`${API_BASE}/variance/${encodeURIComponent(taskId)}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Get variance failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * List confirmed residual tasks for next planning cycle.
   */
  static async getResidualTasks(): Promise<ResidualWorkTask[]> {
    const response = await fetch(`${API_BASE}/residual/tasks`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Get residual tasks failed: ${response.status}`);
    }
    const data = await response.json();
    return data.residual_tasks || [];
  }

  /**
   * List unresolved conflicts in reconciliation queue.
   */
  static async getReconciliationQueue(): Promise<ReconciliationQueueItem[]> {
    const response = await fetch(`${API_BASE}/reconciliation/queue`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Get reconciliation queue failed: ${response.status}`);
    }
    const data = await response.json();
    return data.queue || [];
  }

  /**
   * Resolve a conflict in reconciliation queue.
   */
  static async resolveReconciliationConflict(conflictId: string, notes: string): Promise<ReconciliationQueueItem> {
    const response = await fetch(`${API_BASE}/reconciliation/resolve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conflict_id: conflictId, resolution_notes: notes }),
    });
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Resolve conflict failed: ${response.status}`);
    }
    return response.json();
  }

  /**
   * Generate deterministic estimate review recommendations.
   */
  static async getEstimateReview(): Promise<EstimateReviewResponse> {
    const response = await fetch(`${API_BASE}/estimate-review`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Get estimate review failed: ${response.status}`);
    }
    return response.json();
  }
}
