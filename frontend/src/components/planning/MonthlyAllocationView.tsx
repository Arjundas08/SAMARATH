import React, { useState, useEffect } from 'react';
import { SolveJobApi } from '../../api/solveJobs';
import { MonthlyAllocationPlan, ReconciliationCase } from '../../types/api';
import { Play, AlertTriangle, RefreshCw } from 'lucide-react';

export const MonthlyAllocationView: React.FC = () => {
  const [plan, setPlan] = useState<MonthlyAllocationPlan | null>(null);
  const [reconciliationCases, setReconciliationCases] = useState<ReconciliationCase[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSolving, setIsSolving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMonthlyData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const plans = await SolveJobApi.listMonthlyPlans('VKC');
      if (plans && plans.length > 0) {
        setPlan(plans[0]);
      }
      const cases = await SolveJobApi.getReconciliationCases();
      setReconciliationCases(cases || []);
    } catch (err: any) {
      console.error('Failed to load monthly plan', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMonthlyData();
  }, []);

  const handleGenerateMonthly = async () => {
    setIsSolving(true);
    setError(null);
    try {
      const request = {
        corridor_code: 'VKC',
        planning_month: '2026-10',
        weekly_possession_quota_minutes: 1800,
        bcm_weekly_quota_days: 3,
        csm_weekly_quota_days: 4,
        tw_weekly_quota_days: 5,
        time_limit_seconds: 15.0,
      };
      const result = await SolveJobApi.allocateMonthlyPlan(request);
      setPlan(result);
      await fetchMonthlyData();
    } catch (err: any) {
      setError(err.message || 'Monthly allocation solve failed');
    } finally {
      setIsSolving(false);
    }
  };

  const weekLabels = [
    { idx: 1, title: 'Week 1', dates: '12 Oct - 18 Oct 2026' },
    { idx: 2, title: 'Week 2', dates: '19 Oct - 25 Oct 2026' },
    { idx: 3, title: 'Week 3', dates: '26 Oct - 01 Nov 2026' },
    { idx: 4, title: 'Week 4', dates: '02 Nov - 08 Nov 2026' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Error Alert */}
      {error && (
        <div style={{ backgroundColor: 'var(--color-critical-pale)', color: 'var(--color-critical)', padding: '10px 14px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-critical)', fontSize: '12px' }}>
          {error}
        </div>
      )}

      {/* Top Banner & Allocation Action */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#FFFFFF',
          padding: '16px 20px',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--color-border)',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--color-ink)' }}>
              Tactical 30-Day Monthly Work Allocation (Two-Horizon Planning)
            </h2>
            <span
              style={{
                fontSize: '11px',
                fontWeight: 700,
                color: 'var(--color-warning)',
                backgroundColor: 'var(--color-warning-pale)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid #FCD34D',
              }}
            >
              ALLOCATED_PROVISIONAL
            </span>
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-muted)', marginTop: '2px' }}>
            Tactical weekly quota distribution under Blueprint Sections 20, 21, and 23. Minute-level physical conflict resolution is evaluated in weekly operational solves.
          </div>
        </div>

        <button
          onClick={handleGenerateMonthly}
          disabled={isSolving}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 16px',
            backgroundColor: isSolving ? 'var(--color-muted)' : 'var(--color-action)',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: 'var(--radius-md)',
            fontSize: '12px',
            fontWeight: 600,
            cursor: isSolving ? 'not-allowed' : 'pointer',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          {isSolving ? <RefreshCw size={13} className="spin" /> : <Play size={13} fill="#FFFFFF" />}
          <span>{isSolving ? 'Optimizing Monthly CP-SAT...' : 'Run Tactical Allocation'}</span>
        </button>
      </div>

      {isLoading && (
        <div style={{ fontSize: '11px', color: 'var(--color-muted)', padding: '4px 0' }}>
          Refreshing monthly tactical data...
        </div>
      )}

      {/* Active Reconciliation Warnings Banner */}
      {reconciliationCases.length > 0 && (
        <div
          style={{
            backgroundColor: 'var(--color-warning-pale)',
            border: '1px solid #FCD34D',
            borderRadius: 'var(--radius-md)',
            padding: '12px 16px',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px',
          }}
        >
          <AlertTriangle size={18} color="var(--color-warning)" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-warning)' }}>
              Two-Horizon Reconciliation Variances Detected ({reconciliationCases.length} Cases)
            </div>
            <div style={{ fontSize: '12px', color: 'var(--color-ink)', marginTop: '2px', lineHeight: 1.4 }}>
              The current child weekly schedule contains cross-week shifts or capacity overruns that require formal review by the Operating Reviewer. Approval of the operational weekly programme is blocked until these reconciliation cases are resolved.
            </div>
            <div style={{ display: 'flex', gap: '8px', marginTop: '6px', flexWrap: 'wrap' }}>
              {reconciliationCases.slice(0, 3).map((c) => (
                <span
                  key={c.case_id}
                  style={{
                    fontSize: '11px',
                    fontFamily: 'var(--font-mono)',
                    backgroundColor: '#FFFFFF',
                    padding: '2px 6px',
                    borderRadius: '3px',
                    border: '1px solid #FCD34D',
                  }}
                >
                  {c.business_key}: {c.variance_type} (W{c.allocated_week} → W{c.scheduled_week})
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 4 Calendar Weeks Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px' }}>
        {weekLabels.map((w) => {
          const budget = plan?.quota_budgets.find((b) => b.week_index === w.idx);
          const tasksInWeek = plan?.allocations.filter((a) => a.allocated_week === w.idx) || [];
          const posMinutes = budget?.allocated_possession_minutes || 0;
          const maxMinutes = budget?.max_possession_minutes || 1800;
          const posPct = Math.min(100, Math.round((posMinutes / maxMinutes) * 100));

          return (
            <div
              key={w.idx}
              style={{
                backgroundColor: '#FFFFFF',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--color-border)',
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
              }}
            >
              {/* Card Header */}
              <div
                style={{
                  padding: '12px 14px',
                  backgroundColor: 'var(--color-surface-warm)',
                  borderBottom: '1px solid var(--color-border)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-ink)' }}>
                    {w.title}
                  </div>
                  <span
                    style={{
                      fontSize: '10px',
                      fontFamily: 'var(--font-mono)',
                      fontWeight: 700,
                      backgroundColor: 'var(--color-action-tint)',
                      color: 'var(--color-action)',
                      padding: '1px 6px',
                      borderRadius: '3px',
                    }}
                  >
                    {tasksInWeek.length} Tasks
                  </span>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>
                  {w.dates}
                </div>

                {/* Quota Progress Bar */}
                <div style={{ marginTop: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', marginBottom: '2px' }}>
                    <span style={{ color: 'var(--color-muted)' }}>Possession Quota:</span>
                    <span style={{ fontWeight: 600, color: posPct > 90 ? 'var(--color-critical)' : 'var(--color-ink)' }}>
                      {posMinutes}m / {maxMinutes}m ({posPct}%)
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '5px', backgroundColor: 'var(--color-border)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${posPct}%`,
                        height: '100%',
                        backgroundColor: posPct > 90 ? '#DC2626' : 'var(--color-action)',
                      }}
                    />
                  </div>
                </div>
              </div>

              {/* Task Allocations List */}
              <div style={{ flex: 1, padding: '10px', overflowY: 'auto', maxHeight: '380px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {tasksInWeek.length === 0 ? (
                  <div style={{ padding: '24px 8px', textAlign: 'center', color: 'var(--color-muted)', fontSize: '11px' }}>
                    No tasks allocated to this week.
                  </div>
                ) : (
                  tasksInWeek.map((t) => (
                    <div
                      key={t.task_id}
                      style={{
                        padding: '8px',
                        backgroundColor: 'var(--color-surface-warm)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--color-border)',
                        fontSize: '11px',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
                        <span style={{ fontWeight: 700, color: 'var(--color-ink)' }}>{t.business_key}</span>
                        <span
                          style={{
                            fontSize: '9px',
                            fontWeight: 600,
                            padding: '1px 4px',
                            borderRadius: '2px',
                            backgroundColor:
                              t.department === 'ENGINEERING'
                                ? '#E0F2FE'
                                : t.department === 'ELECTRICAL'
                                ? '#CCFBF1'
                                : '#EDE9FE',
                            color:
                              t.department === 'ENGINEERING'
                                ? '#0369A1'
                                : t.department === 'ELECTRICAL'
                                ? '#0F766E'
                                : '#6D28D9',
                          }}
                        >
                          {t.department === 'ENGINEERING' ? 'CIVIL' : t.department === 'ELECTRICAL' ? 'OHE' : 'S&T'}
                        </span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--color-muted)' }}>
                        <span style={{ fontFamily: 'var(--font-mono)' }}>{t.track_segment_id}</span>
                        <span>{t.duration_minutes}m duration</span>
                      </div>
                      <div style={{ fontSize: '9px', color: 'var(--color-muted)', marginTop: '3px', fontStyle: 'italic' }}>
                        Rationale: {t.allocation_reason.replace('_', ' ')}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
