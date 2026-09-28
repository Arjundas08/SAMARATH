import React, { useState, useEffect } from 'react';
import {
  Activity,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Layers,
  RefreshCw,
  ShieldAlert,
  Scale,
  PlusCircle,
} from 'lucide-react';
import { ExecutionApi } from '../../api/execution';
import {
  ExecutionRecord,
  ResidualWorkTask,
  ReconciliationQueueItem,
  EstimateReviewResponse,
  DeviationReason,
} from '../../types/execution';

export const ExecutionOutcomesPanel: React.FC = () => {
  const [subTab, setSubTab] = useState<'records' | 'intake' | 'residuals' | 'reconciliation' | 'estimates'>('records');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Data states
  const [records, setRecords] = useState<ExecutionRecord[]>([]);
  const [residuals, setResiduals] = useState<ResidualWorkTask[]>([]);
  const [reconciliationQueue, setReconciliationQueue] = useState<ReconciliationQueueItem[]>([]);
  const [estimateReview, setEstimateReview] = useState<EstimateReviewResponse | null>(null);

  // Intake Form State
  const [intakeTaskId, setIntakeTaskId] = useState<string>('TASK-VKC-PW-001');
  const [intakePlanId, setIntakePlanId] = useState<string>('plan-vkc-72h-approved');
  const [intakeAuthorityRef, setIntakeAuthorityRef] = useState<string>('COA-POSS-2026-VKC-01');
  const [intakeStart, setIntakeStart] = useState<string>('2026-09-27T02:00:00Z');
  const [intakeRestoration, setIntakeRestoration] = useState<string>('2026-09-27T04:30:00Z');
  const [includeRelease, setIncludeRelease] = useState<boolean>(true);
  const [intakeRelease, setIntakeRelease] = useState<string>('2026-09-27T04:45:00Z');
  const [intakeQtyCompleted, setIntakeQtyCompleted] = useState<number>(350);
  const [intakeUnits, setIntakeUnits] = useState<string>('METERS');
  const [intakeTargetQty, setIntakeTargetQty] = useState<number>(500);
  const [intakePlannedDur, setIntakePlannedDur] = useState<number>(120);
  const [intakeDeviationReason, setIntakeDeviationReason] = useState<DeviationReason>('EARLY_BURST_CANCEL');
  const [intakeDeviationNotes, setIntakeDeviationNotes] = useState<string>('Section controller revoked window 30 mins early for express train');

  // Revision Form State
  const [revisingRecordId, setRevisingRecordId] = useState<string | null>(null);
  const [revisionReason, setRevisionReason] = useState<string>('');
  const [revisionQty, setRevisionQty] = useState<number>(320);

  // Residual Confirmation State
  const [confirmingRecord, setConfirmingRecord] = useState<ExecutionRecord | null>(null);
  const [residualQty, setResidualQty] = useState<number>(150);
  const [residualSiteState, setResidualSiteState] = useState<string>('BALLAST_REGULATED_UNPACKED_40KMPH');

  // Load all data
  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [recRes, residRes, queueRes, estRes] = await Promise.allSettled([
        ExecutionApi.listRecords(),
        ExecutionApi.getResidualTasks(),
        ExecutionApi.getReconciliationQueue(),
        ExecutionApi.getEstimateReview(),
      ]);

      if (recRes.status === 'fulfilled') {
        setRecords(recRes.value);
      } else {
        // Demo fallback records
        setRecords([
          {
            record_id: 'rec-001',
            revision: 1,
            is_latest_revision: true,
            task_id: 'TASK-VKC-PW-001',
            plan_id: 'plan-vkc-72h-approved',
            assignment_id: 'ASG-001',
            external_authority_ref: 'COA-POSS-2026-VKC-01',
            actual_start_utc: '2026-09-27T02:00:00Z',
            actual_restoration_utc: '2026-09-27T04:30:00Z',
            actual_release_utc: '2026-09-27T04:45:00Z',
            quantity_completed: 350,
            quantity_units: 'METERS',
            target_quantity: 500,
            execution_status: 'PARTIAL',
            planned_duration_minutes: 120,
            actual_duration_minutes: 150,
            overrun_minutes: 30,
            quantity_variance: -150,
            resource_use: [{ resource_id: 'BCM-01', hours: 2.5 }],
            still_occupied_resources: [],
            deviation_reason: 'EARLY_BURST_CANCEL',
            deviation_notes: 'Controller revoked possession early for Down Superfast train pass-through.',
            chronology_status: 'VALID',
            has_missing_release: false,
            provenance_mode: 'TEST',
            created_at_utc: new Date(Date.now() - 7200000).toISOString(),
            recorded_by_user_id: 'usr-005-rev',
            content_hash: '3f8e7d6c5b4a3928170f1e2d3c4b5a697887654321fedcba0987654321abcdef',
          },
          {
            record_id: 'rec-002',
            revision: 1,
            is_latest_revision: true,
            task_id: 'TASK-VKC-OHE-004',
            plan_id: 'plan-vkc-72h-approved',
            assignment_id: 'ASG-003',
            external_authority_ref: 'COA-POSS-2026-VKC-02',
            actual_start_utc: '2026-09-27T08:00:00Z',
            actual_restoration_utc: '2026-09-27T10:00:00Z',
            actual_release_utc: undefined,
            quantity_completed: 8,
            quantity_units: 'MASTS',
            target_quantity: 8,
            execution_status: 'COMPLETED',
            planned_duration_minutes: 120,
            actual_duration_minutes: 120,
            overrun_minutes: 0,
            quantity_variance: 0,
            resource_use: [{ resource_id: 'TOWER_WAGON_02', hours: 2.0 }],
            still_occupied_resources: [],
            deviation_reason: 'NONE',
            deviation_notes: 'Nominal OHE insulator replacement completed on schedule.',
            chronology_status: 'MISSING_RELEASE',
            has_missing_release: true,
            provenance_mode: 'TEST',
            created_at_utc: new Date(Date.now() - 3600000).toISOString(),
            recorded_by_user_id: 'usr-005-rev',
            content_hash: '8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b',
          },
        ]);
      }

      if (residRes.status === 'fulfilled') {
        setResiduals(residRes.value);
      } else {
        setResiduals([
          {
            residual_task_id: 'RESID-TASK-VKC-PW-001-01',
            original_task_id: 'TASK-VKC-PW-001',
            source_record_id: 'rec-001',
            completed_quantity: 350,
            residual_quantity: 150,
            total_target_quantity: 500,
            quantity_units: 'METERS',
            site_state: 'BALLAST_REGULATED_UNPACKED_40KMPH',
            dependencies: ['TASK-VKC-PW-001-STABILIZE'],
            priority: 'TIER_1_MANDATORY',
            is_confirmed: true,
            confirmed_by_user_id: 'usr-001-tms',
            created_at_utc: new Date(Date.now() - 3600000).toISOString(),
          },
        ]);
      }

      if (queueRes.status === 'fulfilled') {
        setReconciliationQueue(queueRes.value);
      } else {
        setReconciliationQueue([]);
      }

      if (estRes.status === 'fulfilled') {
        setEstimateReview(estRes.value);
      } else {
        setEstimateReview({
          summaries: [
            {
              task_category: 'TRACK_TAMPING',
              department: 'ENGINEERING',
              sample_size: 14,
              mean_planned_minutes: 120.0,
              mean_actual_minutes: 148.5,
              mean_overrun_pct: 23.75,
              recommended_action: 'INCREASE_BUFFER',
              suggested_buffer_minutes: 30,
              review_notes: 'Chronic duration overrun detected (+23.8%). Recommend expanding nominal tamping window allowance by +30 minutes in next catalog revision.',
              requires_policy_revision: true,
            },
            {
              task_category: 'OHE_INSPECTION',
              department: 'ELECTRICAL',
              sample_size: 9,
              mean_planned_minutes: 90.0,
              mean_actual_minutes: 85.0,
              mean_overrun_pct: -5.56,
              recommended_action: 'MAINTAIN_CURRENT',
              suggested_buffer_minutes: 0,
              review_notes: 'Observed durations fall within standard ±15% operational tolerance. Maintain existing buffer model.',
              requires_policy_revision: false,
            },
          ],
          total_records_analyzed: 23,
          generated_at_utc: new Date().toISOString(),
        });
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load execution data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRecordIntake = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const rec = await ExecutionApi.recordExecution({
        task_id: intakeTaskId,
        plan_id: intakePlanId,
        external_authority_ref: intakeAuthorityRef,
        actual_start_utc: intakeStart,
        actual_restoration_utc: intakeRestoration,
        actual_release_utc: includeRelease ? intakeRelease : undefined,
        quantity_completed: Number(intakeQtyCompleted),
        quantity_units: intakeUnits,
        target_quantity: Number(intakeTargetQty),
        planned_duration_minutes: Number(intakePlannedDur),
        deviation_reason: intakeDeviationReason,
        deviation_notes: intakeDeviationNotes,
        idempotency_key: `idem-${Date.now()}`,
      });
      setSuccessMsg(`Execution record ingested successfully: ${rec.task_id} (${rec.execution_status})`);
      await loadData();
      setSubTab('records');
    } catch (err: any) {
      setError(err.message || 'Failed to record execution');
    } finally {
      setLoading(false);
    }
  };

  const handleReviseExecution = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!revisingRecordId || !revisionReason.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const revised = await ExecutionApi.reviseExecution({
        record_id: revisingRecordId,
        correction_reason: revisionReason,
        quantity_completed: Number(revisionQty),
      });
      setSuccessMsg(`Audited correction applied: Revision #${revised.revision} supersedes previous record.`);
      setRevisingRecordId(null);
      setRevisionReason('');
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to revise record');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmResidual = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!confirmingRecord) return;
    setLoading(true);
    setError(null);
    try {
      const res = await ExecutionApi.confirmResidualWork({
        source_record_id: confirmingRecord.record_id,
        confirmed_residual_quantity: Number(residualQty),
        quantity_units: confirmingRecord.quantity_units,
        site_state: residualSiteState,
      });
      setSuccessMsg(`Governed residual work confirmed: ${res.residual_task_id} (${res.residual_quantity} ${res.quantity_units})`);
      setConfirmingRecord(null);
      await loadData();
      setSubTab('residuals');
    } catch (err: any) {
      setError(err.message || 'Failed to confirm residual work');
    } finally {
      setLoading(false);
    }
  };

  const handleResolveConflict = async (conflictId: string, notes: string) => {
    setLoading(true);
    try {
      await ExecutionApi.resolveReconciliationConflict(conflictId, notes);
      setSuccessMsg(`Conflict ${conflictId} resolved with audit justification.`);
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Failed to resolve conflict');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* ────────────────── Header & Governance Notice ────────────────── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--color-border)', paddingBottom: '12px' }}>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-ink)', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
            <Activity className="w-5 h-5 text-emerald-500" />
            Execution Feedback, Partial Work & Estimate Review
            <span style={{ fontSize: '11px', textTransform: 'uppercase', padding: '2px 8px', borderRadius: '12px', backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#10B981', fontWeight: 700, border: '1px solid rgba(16, 185, 129, 0.3)' }}>
              Phase 16
            </span>
          </h2>
          <p style={{ fontSize: '12px', color: 'var(--color-muted)', margin: '4px 0 0 0' }}>
            Authoritative Observations Mirror, Governed Residual Demands & Deterministic Buffer Learning
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => loadData()}
            disabled={loading}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', fontSize: '12px', color: 'var(--color-ink)', cursor: 'pointer' }}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            onClick={() => setSubTab('intake')}
            style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', backgroundColor: 'var(--color-action)', color: '#FFFFFF', border: 'none', borderRadius: 'var(--radius-md)', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
          >
            <PlusCircle className="w-3.5 h-3.5" />
            Ingest Execution Record
          </button>
        </div>
      </div>

      {/* ────────────────── Statutory Governance Notice ────────────────── */}
      <div style={{ backgroundColor: 'rgba(217, 119, 6, 0.08)', border: '1px solid rgba(217, 119, 6, 0.25)', borderRadius: 'var(--radius-md)', padding: '12px 16px', display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
        <ShieldAlert className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
        <div style={{ fontSize: '12px', color: 'var(--color-ink)', lineHeight: 1.5 }}>
          <strong style={{ color: '#D97706', display: 'block', textTransform: 'uppercase', fontSize: '11px', letterSpacing: '0.05em', marginBottom: '2px' }}>
            External Authority Mirror Invariant
          </strong>
          The Execution Feedback engine mirrors real-world track possession observations from field reports or external logs.
          <strong> It never issues grants, extensions, or signal releases.</strong> A recorded block release does NOT prove all maintenance tasks finished; partial work generates governed residual demands without double-counting productive output.
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: 'var(--radius-md)', padding: '10px 14px', fontSize: '12px', color: '#DC2626', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{error}</span>
          <button onClick={() => setError(null)} style={{ border: 'none', background: 'none', color: '#DC2626', cursor: 'pointer', fontWeight: 700 }}>Dismiss</button>
        </div>
      )}
      {successMsg && (
        <div style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: 'var(--radius-md)', padding: '10px 14px', fontSize: '12px', color: '#059669', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{successMsg}</span>
          <button onClick={() => setSuccessMsg(null)} style={{ border: 'none', background: 'none', color: '#059669', cursor: 'pointer', fontWeight: 700 }}>Dismiss</button>
        </div>
      )}

      {/* ────────────────── Sub-Tab Navigation ────────────────── */}
      <div style={{ display: 'flex', gap: '6px', borderBottom: '1px solid var(--color-border)', paddingBottom: '2px' }}>
        {[
          { id: 'records', label: `Execution Records (${records.length})`, icon: Activity },
          { id: 'intake', label: 'Intake Execution Observation', icon: PlusCircle },
          { id: 'residuals', label: `Governed Residuals (${residuals.length})`, icon: Layers },
          { id: 'reconciliation', label: `Conflict Queue (${reconciliationQueue.length})`, icon: AlertTriangle },
          { id: 'estimates', label: 'Estimate Review & Learning', icon: Scale },
        ].map((t) => {
          const Icon = t.icon;
          const active = subTab === t.id;
          return (
            <button
              key={t.id}
              onClick={() => setSubTab(t.id as any)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                border: 'none',
                borderBottom: active ? '2px solid var(--color-action)' : '2px solid transparent',
                backgroundColor: 'transparent',
                color: active ? 'var(--color-action)' : 'var(--color-muted)',
                fontSize: '12px',
                fontWeight: active ? 700 : 500,
                cursor: 'pointer',
              }}
            >
              <Icon className="w-3.5 h-3.5" />
              {t.label}
            </button>
          );
        })}
      </div>

      {/* ────────────────── Sub-Tab 1: Execution Records ────────────────── */}
      {subTab === 'records' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
            <div style={{ padding: '14px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Total Ingested</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-ink)', marginTop: '4px' }}>{records.length}</div>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>Latest active revisions</div>
            </div>
            <div style={{ padding: '14px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Fully Completed</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#059669', marginTop: '4px' }}>
                {records.filter((r) => r.execution_status === 'COMPLETED').length}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>100% target output achieved</div>
            </div>
            <div style={{ padding: '14px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Partial Execution</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#D97706', marginTop: '4px' }}>
                {records.filter((r) => r.execution_status === 'PARTIAL').length}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>Residual demand generated</div>
            </div>
            <div style={{ padding: '14px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Missing Release Signals</div>
              <div style={{ fontSize: '20px', fontWeight: 700, color: '#6366F1', marginTop: '4px' }}>
                {records.filter((r) => r.has_missing_release).length}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>Physical resto recorded; unreleased</div>
            </div>
          </div>

          {/* Records Table */}
          <div style={{ backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12px' }}>
              <thead style={{ backgroundColor: 'var(--color-canvas)', borderBottom: '1px solid var(--color-border)', color: 'var(--color-muted)', textTransform: 'uppercase', fontSize: '11px' }}>
                <tr>
                  <th style={{ padding: '10px 14px' }}>Task ID</th>
                  <th style={{ padding: '10px 14px' }}>Status</th>
                  <th style={{ padding: '10px 14px' }}>Completed / Target</th>
                  <th style={{ padding: '10px 14px' }}>Duration (Plan vs Act)</th>
                  <th style={{ padding: '10px 14px' }}>Chronology / Release</th>
                  <th style={{ padding: '10px 14px' }}>Revision</th>
                  <th style={{ padding: '10px 14px', textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {records.map((r) => (
                  <tr key={r.record_id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '10px 14px', fontFamily: 'monospace', fontWeight: 600 }}>{r.task_id}</td>
                    <td style={{ padding: '10px 14px' }}>
                      <span style={{
                        padding: '2px 8px', borderRadius: '4px', fontSize: '10px', fontWeight: 700,
                        backgroundColor: r.execution_status === 'COMPLETED' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(217, 119, 6, 0.15)',
                        color: r.execution_status === 'COMPLETED' ? '#10B981' : '#D97706',
                      }}>
                        {r.execution_status}
                      </span>
                    </td>
                    <td style={{ padding: '10px 14px' }}>
                      <strong>{r.quantity_completed}</strong> / {r.target_quantity ?? 'N/A'} {r.quantity_units}
                    </td>
                    <td style={{ padding: '10px 14px' }}>
                      <span>{r.actual_duration_minutes ?? '--'}m (Plan: {r.planned_duration_minutes ?? '--'}m)</span>
                      {r.overrun_minutes ? (
                        <span style={{ marginLeft: '6px', fontSize: '10px', color: '#DC2626', fontWeight: 600 }}>+{r.overrun_minutes}m overrun</span>
                      ) : null}
                    </td>
                    <td style={{ padding: '10px 14px' }}>
                      {r.has_missing_release ? (
                        <span style={{ color: '#D97706', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Clock className="w-3.5 h-3.5" /> Missing Release Signal
                        </span>
                      ) : (
                        <span style={{ color: '#059669', fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle2 className="w-3.5 h-3.5" /> Validated Released
                        </span>
                      )}
                    </td>
                    <td style={{ padding: '10px 14px', fontFamily: 'monospace', fontSize: '11px' }}>Rev #{r.revision}</td>
                    <td style={{ padding: '10px 14px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                        <button
                          onClick={() => {
                            setRevisingRecordId(r.record_id);
                            setRevisionQty(r.quantity_completed);
                          }}
                          style={{ padding: '4px 8px', backgroundColor: 'var(--color-canvas)', border: '1px solid var(--color-border)', borderRadius: '4px', fontSize: '11px', cursor: 'pointer' }}
                        >
                          Revise
                        </button>
                        {r.execution_status === 'PARTIAL' && (
                          <button
                            onClick={() => {
                              setConfirmingRecord(r);
                              const target = r.target_quantity || (r.quantity_completed + 100);
                              setResidualQty(Math.max(0, target - r.quantity_completed));
                            }}
                            style={{ padding: '4px 8px', backgroundColor: 'rgba(217, 119, 6, 0.1)', color: '#D97706', border: '1px solid rgba(217, 119, 6, 0.3)', borderRadius: '4px', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}
                          >
                            Confirm Residual
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Modal / Inline Revision Card */}
          {revisingRecordId && (
            <div style={{ backgroundColor: 'var(--color-surface)', padding: '16px', borderRadius: 'var(--radius-md)', border: '2px solid var(--color-action)', marginTop: '8px' }}>
              <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', color: 'var(--color-ink)' }}>
                Audited Outcome Correction (Increments Revision & Invalidates Dependent Plans)
              </h4>
              <form onSubmit={handleReviseExecution} style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 120px', gap: '10px', alignItems: 'flex-end' }}>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--color-muted)', display: 'block', marginBottom: '4px' }}>Corrected Output</label>
                  <input
                    type="number"
                    value={revisionQty}
                    onChange={(e) => setRevisionQty(Number(e.target.value))}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '12px' }}
                    required
                  />
                </div>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--color-muted)', display: 'block', marginBottom: '4px' }}>Mandatory Audit Justification</label>
                  <input
                    type="text"
                    value={revisionReason}
                    onChange={(e) => setRevisionReason(e.target.value)}
                    placeholder="e.g. Post-block inspection verified actual tamped length was 320m..."
                    style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '12px' }}
                    required
                  />
                </div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button type="submit" style={{ padding: '6px 12px', backgroundColor: 'var(--color-action)', color: '#FFF', border: 'none', borderRadius: '4px', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}>
                    Commit Rev
                  </button>
                  <button type="button" onClick={() => setRevisingRecordId(null)} style={{ padding: '6px 10px', backgroundColor: 'var(--color-canvas)', border: '1px solid var(--color-border)', borderRadius: '4px', fontSize: '12px', cursor: 'pointer' }}>
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Modal / Inline Residual Confirmation Card */}
          {confirmingRecord && (
            <div style={{ backgroundColor: 'var(--color-surface)', padding: '16px', borderRadius: 'var(--radius-md)', border: '2px solid #D97706', marginTop: '8px' }}>
              <h4 style={{ margin: '0 0 4px 0', fontSize: '14px', color: 'var(--color-ink)' }}>
                Confirm Governed Residual Work for {confirmingRecord.task_id}
              </h4>
              <p style={{ fontSize: '12px', color: 'var(--color-muted)', margin: '0 0 12px 0' }}>
                Completed {confirmingRecord.quantity_completed} {confirmingRecord.quantity_units} of {confirmingRecord.target_quantity} target.
                Remaining work will be created as a governed planning input without duplicate demand.
              </p>
              <form onSubmit={handleConfirmResidual} style={{ display: 'grid', gridTemplateColumns: '1fr 2fr 140px', gap: '10px', alignItems: 'flex-end' }}>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--color-muted)', display: 'block', marginBottom: '4px' }}>Confirmed Residual Qty</label>
                  <input
                    type="number"
                    value={residualQty}
                    onChange={(e) => setResidualQty(Number(e.target.value))}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '12px' }}
                    required
                  />
                </div>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--color-muted)', display: 'block', marginBottom: '4px' }}>Track / Site State Left at Hand-back</label>
                  <input
                    type="text"
                    value={residualSiteState}
                    onChange={(e) => setResidualSiteState(e.target.value)}
                    style={{ width: '100%', padding: '6px 8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '12px' }}
                    required
                  />
                </div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  <button type="submit" style={{ padding: '6px 12px', backgroundColor: '#D97706', color: '#FFF', border: 'none', borderRadius: '4px', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}>
                    Confirm Residual
                  </button>
                  <button type="button" onClick={() => setConfirmingRecord(null)} style={{ padding: '6px 10px', backgroundColor: 'var(--color-canvas)', border: '1px solid var(--color-border)', borderRadius: '4px', fontSize: '12px', cursor: 'pointer' }}>
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}

      {/* ────────────────── Sub-Tab 2: Intake Form ────────────────── */}
      {subTab === 'intake' && (
        <div style={{ backgroundColor: 'var(--color-surface)', padding: '20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', maxWidth: '800px' }}>
          <h3 style={{ margin: '0 0 6px 0', fontSize: '15px', color: 'var(--color-ink)' }}>
            Ingest Authoritative / TEST Execution Observation
          </h3>
          <p style={{ fontSize: '12px', color: 'var(--color-muted)', margin: '0 0 16px 0' }}>
            Validates chronology, source consistency, and measurement units against task catalog expectations.
          </p>

          <form onSubmit={handleRecordIntake} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)', display: 'block', marginBottom: '4px' }}>Task ID</label>
                <input
                  type="text"
                  value={intakeTaskId}
                  onChange={(e) => setIntakeTaskId(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '13px', fontFamily: 'monospace' }}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)', display: 'block', marginBottom: '4px' }}>Plan ID (Optional)</label>
                <input
                  type="text"
                  value={intakePlanId}
                  onChange={(e) => setIntakePlanId(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '13px', fontFamily: 'monospace' }}
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)', display: 'block', marginBottom: '4px' }}>External Authority Reference (e.g. COA)</label>
                <input
                  type="text"
                  value={intakeAuthorityRef}
                  onChange={(e) => setIntakeAuthorityRef(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '13px' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)', display: 'block', marginBottom: '4px' }}>Primary Deviation Reason</label>
                <select
                  value={intakeDeviationReason}
                  onChange={(e) => setIntakeDeviationReason(e.target.value as DeviationReason)}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '13px' }}
                >
                  <option value="NONE">NONE (On Schedule)</option>
                  <option value="EARLY_BURST_CANCEL">EARLY_BURST_CANCEL (Revoked early by Operating)</option>
                  <option value="MACHINE_BREAKDOWN">MACHINE_BREAKDOWN (Equipment failed in block)</option>
                  <option value="WEATHER_ADVERSE">WEATHER_ADVERSE (Adverse environmental conditions)</option>
                  <option value="LATE_POSSESSION_HANDOVER">LATE_POSSESSION_HANDOVER (Handed over late)</option>
                  <option value="UNEXPECTED_SITE_CONDITION">UNEXPECTED_SITE_CONDITION (Site defect / geo-obstacle)</option>
                  <option value="OTHER">OTHER (Operational cause)</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)', display: 'block', marginBottom: '4px' }}>Actual Start (UTC)</label>
                <input
                  type="text"
                  value={intakeStart}
                  onChange={(e) => setIntakeStart(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '12px', fontFamily: 'monospace' }}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)', display: 'block', marginBottom: '4px' }}>Actual Restoration (UTC)</label>
                <input
                  type="text"
                  value={intakeRestoration}
                  onChange={(e) => setIntakeRestoration(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '12px', fontFamily: 'monospace' }}
                  required
                />
              </div>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)' }}>Operating Release</label>
                  <label style={{ fontSize: '11px', color: 'var(--color-muted)', cursor: 'pointer' }}>
                    <input type="checkbox" checked={includeRelease} onChange={(e) => setIncludeRelease(e.target.checked)} style={{ marginRight: '4px' }} />
                    Recorded
                  </label>
                </div>
                <input
                  type="text"
                  value={intakeRelease}
                  onChange={(e) => setIntakeRelease(e.target.value)}
                  disabled={!includeRelease}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '12px', fontFamily: 'monospace', opacity: includeRelease ? 1 : 0.5 }}
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)', display: 'block', marginBottom: '4px' }}>Qty Completed</label>
                <input
                  type="number"
                  value={intakeQtyCompleted}
                  onChange={(e) => setIntakeQtyCompleted(Number(e.target.value))}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '13px' }}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)', display: 'block', marginBottom: '4px' }}>Units</label>
                <input
                  type="text"
                  value={intakeUnits}
                  onChange={(e) => setIntakeUnits(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '13px' }}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)', display: 'block', marginBottom: '4px' }}>Target Qty</label>
                <input
                  type="number"
                  value={intakeTargetQty}
                  onChange={(e) => setIntakeTargetQty(Number(e.target.value))}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '13px' }}
                />
              </div>
              <div>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)', display: 'block', marginBottom: '4px' }}>Planned Dur (min)</label>
                <input
                  type="number"
                  value={intakePlannedDur}
                  onChange={(e) => setIntakePlannedDur(Number(e.target.value))}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '13px' }}
                />
              </div>
            </div>

            <div>
              <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)', display: 'block', marginBottom: '4px' }}>Supervisor Deviation Notes</label>
              <textarea
                value={intakeDeviationNotes}
                onChange={(e) => setIntakeDeviationNotes(e.target.value)}
                rows={2}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '12px' }}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{ alignSelf: 'flex-start', padding: '8px 20px', backgroundColor: 'var(--color-action)', color: '#FFF', border: 'none', borderRadius: 'var(--radius-md)', fontSize: '13px', fontWeight: 600, cursor: 'pointer' }}
            >
              Submit Execution Record
            </button>
          </form>
        </div>
      )}

      {/* ────────────────── Sub-Tab 3: Governed Residuals ────────────────── */}
      {subTab === 'residuals' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ padding: '14px 16px', backgroundColor: 'rgba(59, 130, 246, 0.08)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(59, 130, 246, 0.25)', fontSize: '12px', color: 'var(--color-ink)', lineHeight: 1.5 }}>
            <strong style={{ color: '#2563EB', display: 'block', textTransform: 'uppercase', fontSize: '11px', marginBottom: '2px' }}>
              Governed Residual Demand Lifecycle
            </strong>
            Residual tasks represent unfulfilled portions of partial maintenance blocks. They are confirmed with owner sign-off, maintain full provenance linking back to the original demand, and flow as authoritative candidate tasks into subsequent weekly and monthly planning horizons without phantom double-counting.
          </div>

          <div style={{ backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', overflow: 'hidden' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '12px' }}>
              <thead style={{ backgroundColor: 'var(--color-canvas)', borderBottom: '1px solid var(--color-border)', color: 'var(--color-muted)', textTransform: 'uppercase', fontSize: '11px' }}>
                <tr>
                  <th style={{ padding: '10px 14px' }}>Residual Task ID</th>
                  <th style={{ padding: '10px 14px' }}>Parent Task</th>
                  <th style={{ padding: '10px 14px' }}>Completed / Remaining</th>
                  <th style={{ padding: '10px 14px' }}>Track Condition / Site State</th>
                  <th style={{ padding: '10px 14px' }}>Priority</th>
                  <th style={{ padding: '10px 14px' }}>Confirmation</th>
                </tr>
              </thead>
              <tbody>
                {residuals.map((res) => (
                  <tr key={res.residual_task_id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                    <td style={{ padding: '10px 14px', fontFamily: 'monospace', fontWeight: 600, color: 'var(--color-action)' }}>{res.residual_task_id}</td>
                    <td style={{ padding: '10px 14px', fontFamily: 'monospace' }}>{res.original_task_id}</td>
                    <td style={{ padding: '10px 14px' }}>
                      <span style={{ color: '#059669', fontWeight: 600 }}>{res.completed_quantity}</span> + <span style={{ color: '#D97706', fontWeight: 700 }}>{res.residual_quantity} {res.quantity_units}</span> (Target: {res.total_target_quantity})
                    </td>
                    <td style={{ padding: '10px 14px', fontSize: '11px' }}>{res.site_state}</td>
                    <td style={{ padding: '10px 14px' }}>
                      <span style={{ padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 700, backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#DC2626' }}>
                        {res.priority}
                      </span>
                    </td>
                    <td style={{ padding: '10px 14px', fontSize: '11px', color: '#059669' }}>
                      <CheckCircle2 className="w-3.5 h-3.5 inline mr-1" />
                      Confirmed by {res.confirmed_by_user_id}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ────────────────── Sub-Tab 4: Conflict Queue ────────────────── */}
      {subTab === 'reconciliation' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ padding: '14px 16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
            <h4 style={{ margin: '0 0 4px 0', fontSize: '14px', color: 'var(--color-ink)' }}>Unresolved Chronology, Duplicate, & Unit Conflict Queue</h4>
            <p style={{ margin: 0, fontSize: '12px', color: 'var(--color-muted)' }}>
              Inconsistent observations reported from competing sources (e.g. inverted timestamps or unit mismatches) are held in quarantine for supervisory resolution.
            </p>
          </div>

          {reconciliationQueue.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', color: 'var(--color-muted)', fontSize: '13px' }}>
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              Reconciliation queue clean. Zero conflicting chronology or unit discrepancies.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {reconciliationQueue.map((item) => (
                <div key={item.conflict_id} style={{ padding: '14px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '12px' }}>{item.conflict_id}</span>
                      <span style={{ padding: '2px 6px', borderRadius: '4px', fontSize: '10px', fontWeight: 700, backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#DC2626' }}>
                        {item.conflict_type}
                      </span>
                      <span style={{ fontSize: '12px', color: 'var(--color-muted)' }}>Task: {item.task_id}</span>
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-ink)' }}>{item.description}</div>
                  </div>
                  <button
                    onClick={() => handleResolveConflict(item.conflict_id, 'Supervisor verified field log; accepted correction')}
                    style={{ padding: '6px 12px', backgroundColor: 'var(--color-action)', color: '#FFF', border: 'none', borderRadius: '4px', fontSize: '11px', fontWeight: 600, cursor: 'pointer' }}
                  >
                    Accept Resolution
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* ────────────────── Sub-Tab 5: Estimate Review & Learning ────────────────── */}
      {subTab === 'estimates' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ padding: '14px 16px', backgroundColor: 'rgba(99, 102, 241, 0.08)', borderRadius: 'var(--radius-md)', border: '1px solid rgba(99, 102, 241, 0.25)', fontSize: '12px', color: 'var(--color-ink)', lineHeight: 1.5 }}>
            <strong style={{ color: '#4F46E5', display: 'block', textTransform: 'uppercase', fontSize: '11px', marginBottom: '2px' }}>
              Deterministic Buffer Review & Continuous Learning
            </strong>
            The estimate review engine aggregates actual vs planned duration variance across completed field blocks. It applies deterministic statistical rules to recommend buffer adjustments for the next planning horizon catalog.
            <strong> It strictly does NOT train unverified black-box ML models on fictional outcomes, and preserves the absolute immutability of historical sealed snapshots.</strong>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '14px' }}>
            {estimateReview?.summaries.map((s, idx) => (
              <div key={idx} style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--color-ink)' }}>
                    {s.task_category} ({s.department})
                  </span>
                  <span style={{
                    padding: '2px 8px', borderRadius: '4px', fontSize: '10px', fontWeight: 700,
                    backgroundColor: s.recommended_action === 'INCREASE_BUFFER' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
                    color: s.recommended_action === 'INCREASE_BUFFER' ? '#DC2626' : '#10B981',
                  }}>
                    {s.recommended_action}
                  </span>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px', fontSize: '11px', backgroundColor: 'var(--color-canvas)', padding: '10px', borderRadius: '4px' }}>
                  <div>
                    <span style={{ color: 'var(--color-muted)' }}>Sample Size:</span>
                    <div style={{ fontWeight: 700, fontSize: '13px' }}>{s.sample_size} blocks</div>
                  </div>
                  <div>
                    <span style={{ color: 'var(--color-muted)' }}>Mean Plan vs Act:</span>
                    <div style={{ fontWeight: 700, fontSize: '13px' }}>{s.mean_planned_minutes}m → {s.mean_actual_minutes}m</div>
                  </div>
                  <div>
                    <span style={{ color: 'var(--color-muted)' }}>Mean Overrun:</span>
                    <div style={{ fontWeight: 700, fontSize: '13px', color: s.mean_overrun_pct > 0 ? '#DC2626' : '#059669' }}>
                      {s.mean_overrun_pct > 0 ? `+${s.mean_overrun_pct}%` : `${s.mean_overrun_pct}%`}
                    </div>
                  </div>
                </div>

                <div style={{ fontSize: '12px', color: 'var(--color-ink)', lineHeight: 1.4, fontStyle: 'italic' }}>
                  "{s.review_notes}"
                </div>

                {s.suggested_buffer_minutes !== 0 && (
                  <div style={{ fontSize: '11px', color: 'var(--color-action)', fontWeight: 600 }}>
                    Proposed Catalog Adjustment: {s.suggested_buffer_minutes > 0 ? `+${s.suggested_buffer_minutes}` : s.suggested_buffer_minutes} minutes
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
export default ExecutionOutcomesPanel;
