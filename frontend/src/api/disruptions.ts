/**
 * Phase 13: Disruption Events, Stable Replanning & PlanDiff API client.
 * Blueprint Sections: 27-28, 34 plus addendum.
 */
import {
  DisruptionEvent,
  DisruptionEventCreate,
  PlanDiffResponse,
  PlanDiffSummary,
  ImpactClosureResponse,
  StableReplanRequest,
  StableReplanResponse,
  EscalationCheckResponse,
} from '../types/disruptions';

const API_BASE = '/api/v1/disruptions';

export class DisruptionApi {
  /**
   * Submits a disruption event with monotonic ordering and idempotency.
   */
  static async submitEvent(event: DisruptionEventCreate): Promise<DisruptionEvent> {
    const response = await fetch(`${API_BASE}/events`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(event),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Event submission failed with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Lists disruption events for a corridor.
   */
  static async listEvents(
    corridorCode: string = 'VKC',
    limit: number = 50
  ): Promise<{ events: DisruptionEvent[]; total: number; corridor_code: string }> {
    const params = new URLSearchParams({
      corridor_code: corridorCode,
      limit: String(limit),
    });

    const response = await fetch(`${API_BASE}/events?${params.toString()}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Listing events failed with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Lists pending (unresolved) disruption events for a corridor.
   */
  static async listPendingEvents(
    corridorCode: string = 'VKC'
  ): Promise<{ events: DisruptionEvent[]; total: number; corridor_code: string }> {
    const params = new URLSearchParams({ corridor_code: corridorCode });
    const response = await fetch(`${API_BASE}/events/pending?${params.toString()}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Listing pending events failed with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Computes impact closure for a set of disruption events.
   */
  static async computeImpactClosure(
    eventIds: string[],
    baselinePlanId?: string
  ): Promise<ImpactClosureResponse> {
    const url = baselinePlanId
      ? `${API_BASE}/impact-closure?baseline_plan_id=${encodeURIComponent(baselinePlanId)}`
      : `${API_BASE}/impact-closure`;

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(eventIds),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Impact closure computation failed with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Computes minute-exact PlanDiff between two plan revisions.
   */
  static async computePlanDiff(
    fromPlanId: string,
    toPlanId: string,
    diffReason?: string
  ): Promise<PlanDiffResponse> {
    const response = await fetch(`${API_BASE}/plandiff`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from_plan_id: fromPlanId,
        to_plan_id: toPlanId,
        diff_reason: diffReason,
      }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `PlanDiff computation failed with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Fetches stored PlanDiffs associated with a plan.
   */
  static async getPlanDiffs(
    planId: string
  ): Promise<{ plan_id: string; diffs: PlanDiffSummary[] }> {
    const response = await fetch(`${API_BASE}/plandiff/${encodeURIComponent(planId)}`);
    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Failed to fetch plan diffs with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Triggers minimal-churn DISRUPTION_RECOVERY replan.
   */
  static async triggerStableReplan(
    request: StableReplanRequest
  ): Promise<StableReplanResponse> {
    const response = await fetch(`${API_BASE}/replan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Stable replan trigger failed with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Checks for hard lock conflicts requiring escalation.
   */
  static async checkLockEscalation(
    planId: string
  ): Promise<EscalationCheckResponse> {
    const response = await fetch(
      `${API_BASE}/replan/check-escalation?plan_id=${encodeURIComponent(planId)}`,
      { method: 'POST' }
    );

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Lock escalation check failed with status ${response.status}`);
    }

    return response.json();
  }
}
