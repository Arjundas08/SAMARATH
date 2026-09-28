/**
 * Phase 14: Evaluation, Calculated Metrics & Stress Scenarios API Client.
 * Blueprint Sections: 26, 37-40.
 */
import {
  CalculatedPlanMetrics,
  FairComparisonResult,
  FixedPlanStressReport,
  AdaptiveStressRecoveryResult,
  StressPerturbation,
} from '../types/evaluation';

const API_BASE = '/api/v1/evaluation';

export class EvaluationApi {
  /**
   * Fetches the 10 declared versioned stress test scenarios.
   */
  static async getDeclaredScenarios(): Promise<StressPerturbation[]> {
    const response = await fetch(`${API_BASE}/scenarios`);
    if (!response.ok) {
      throw new Error(`Failed to fetch scenarios: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Calculates versioned pinned metrics for a plan.
   */
  static async calculatePlanMetrics(params: {
    planId?: string;
    planData?: any;
    snapshotData?: any;
    rulePolicyVersion?: string;
    domainVersion?: string;
  }): Promise<CalculatedPlanMetrics> {
    const query = params.planId ? `?plan_id=${encodeURIComponent(params.planId)}` : '';
    const body: Record<string, any> = {};
    if (params.planData) body.plan_data = params.planData;
    if (params.snapshotData) body.snapshot_data = params.snapshotData;
    if (params.rulePolicyVersion) body.rule_policy_version = params.rulePolicyVersion;
    if (params.domainVersion) body.domain_version = params.domainVersion;

    const response = await fetch(`${API_BASE}/metrics/calculate${query}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Metrics calculation failed with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Conducts defensible fair comparison between baseline and candidate plans.
   */
  static async comparePlans(params: {
    baselinePlanId?: string;
    candidatePlanId?: string;
    baselinePlan?: any;
    candidatePlan?: any;
    snapshot?: any;
  }): Promise<FairComparisonResult> {
    const body: Record<string, any> = {};
    if (params.baselinePlanId) body.baseline_plan_id = params.baselinePlanId;
    if (params.candidatePlanId) body.candidate_plan_id = params.candidatePlanId;
    if (params.baselinePlan) body.baseline_plan = params.baselinePlan;
    if (params.candidatePlan) body.candidate_plan = params.candidatePlan;
    if (params.snapshot) body.snapshot = params.snapshot;

    const response = await fetch(`${API_BASE}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Fair comparison failed with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Executes fixed-plan stress test across all 4 perturbation types.
   */
  static async runFixedPlanStressTest(params: {
    planId?: string;
    planData?: any;
    snapshotData?: any;
  }): Promise<FixedPlanStressReport> {
    const query = params.planId ? `?plan_id=${encodeURIComponent(params.planId)}` : '';
    const body: Record<string, any> = {};
    if (params.planData) body.plan_data = params.planData;
    if (params.snapshotData) body.snapshot_data = params.snapshotData;

    const response = await fetch(`${API_BASE}/stress-test${query}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Stress testing failed with status ${response.status}`);
    }

    return response.json();
  }

  /**
   * Runs adaptive recovery experiment under perturbed snapshot.
   */
  static async runAdaptiveRecovery(params: {
    planId?: string;
    planData?: any;
    snapshotData?: any;
  }): Promise<AdaptiveStressRecoveryResult> {
    const query = params.planId ? `?plan_id=${encodeURIComponent(params.planId)}` : '';
    const body: Record<string, any> = {};
    if (params.planData) body.plan_data = params.planData;
    if (params.snapshotData) body.snapshot_data = params.snapshotData;

    const response = await fetch(`${API_BASE}/adaptive-stress-test${query}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(err.detail || `Adaptive recovery failed with status ${response.status}`);
    }

    return response.json();
  }
}
