/**
 * Phase 17 – Failure Recovery, Security & Scaling Evidence API Client.
 * Blueprint Sections: 33-34, 41-43, 51, 55-58.
 */
import {
  ResilienceDashboardResponse,
  WorkloadBenchmarkSummary,
  FailureScenarioResult,
  SecurityAuditItem,
  BackupRestoreDrillReport,
  BenchmarkStageMetrics,
} from '../types/resilience';

const API_BASE = '/api/v1/resilience';

export class ResilienceApi {
  /**
   * Fetches the complete Resilience & Scaling Evidence Dashboard bundle.
   */
  static async getDashboard(): Promise<ResilienceDashboardResponse> {
    const response = await fetch(`${API_BASE}/dashboard`);
    if (!response.ok) {
      throw new Error(`Failed to fetch resilience dashboard: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Fetches workload scaling benchmarks.
   */
  static async getBenchmarks(): Promise<WorkloadBenchmarkSummary[]> {
    const response = await fetch(`${API_BASE}/benchmarks`);
    if (!response.ok) {
      throw new Error(`Failed to fetch scaling benchmarks: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Triggers a live benchmark run for a specific task size.
   */
  static async runBenchmark(tasks: number = 30, seed: number = 42): Promise<BenchmarkStageMetrics> {
    const response = await fetch(`${API_BASE}/benchmarks/run?tasks=${tasks}&seed=${seed}`, {
      method: 'POST',
    });
    if (!response.ok) {
      throw new Error(`Failed to execute benchmark run: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Fetches failure injection scenario results.
   */
  static async getFailureInjectionResults(): Promise<FailureScenarioResult[]> {
    const response = await fetch(`${API_BASE}/failure-injection`);
    if (!response.ok) {
      throw new Error(`Failed to fetch failure injection results: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Fetches itemized security audit checklist.
   */
  static async getSecurityAudit(): Promise<SecurityAuditItem[]> {
    const response = await fetch(`${API_BASE}/security/audit`);
    if (!response.ok) {
      throw new Error(`Failed to fetch security audit: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Fetches or triggers backup and restoration drill report.
   */
  static async getBackupRestoreDrill(): Promise<BackupRestoreDrillReport> {
    const response = await fetch(`${API_BASE}/backup-drill`);
    if (!response.ok) {
      throw new Error(`Failed to fetch backup restore drill: ${response.statusText}`);
    }
    return response.json();
  }
}
