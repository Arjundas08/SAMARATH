import React, { useState, useEffect } from 'react';
import { ProvenanceBadge } from '../components/common/ProvenanceBadge';


interface DeclarativeRule {
  rule_id: string;
  revision: number;
  department_a: string;
  work_type_a: string;
  department_b: string;
  work_type_b: string;
  effect: 'ALLOWED' | 'PROHIBITED' | 'UNKNOWN';
  requires_concurrent_execution: boolean;
  requires_sequential_execution: boolean;
  description: string;
  evidence_reference: string;
  author: string;
  approver: string;
  effective_from_utc: string;
  effective_to_utc: string | null;
  superseded_by_revision: number | null;
}

interface PackagePhase {
  phase_type: string;
  duration_minutes: number;
  offset_start_minutes: number;
  offset_end_minutes: number;
  description: string;
}

interface WorkPackageFixture {
  package_id: string;
  business_keys: string[];
  departments: string[];
  track_segment_id: string;
  chainage_start_km: number;
  chainage_end_km: number;
  compatibility_verdict: string;
  cumulative_capacity_required: number;
  available_capacity: number;
  is_eligible: boolean;
  ineligibility_reason: string | null;
  recipe: {
    recipe_id: string;
    name: string;
    total_duration_minutes: number;
    is_sequential: boolean;
    phases: PackagePhase[];
    assumption_badge: string;
  };
}

export const RulesView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'rules' | 'calculator' | 'fixtures'>('rules');
  const [rules, setRules] = useState<DeclarativeRule[]>([]);
  const [fixtures, setFixtures] = useState<WorkPackageFixture[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterEffect, setFilterEffect] = useState<string>('ALL');

  // Verify Modal State
  const [selectedRule, setSelectedRule] = useState<DeclarativeRule | null>(null);
  const [verifyEffect, setVerifyEffect] = useState<'ALLOWED' | 'PROHIBITED' | 'UNKNOWN'>('ALLOWED');
  const [verifyEvidence, setVerifyEvidence] = useState('');
  const [verifyNotes, setVerifyNotes] = useState('');
  const [verifyOfficer, setVerifyOfficer] = useState('Principal Chief Engineer');
  const [verifySuccess, setVerifySuccess] = useState<string | null>(null);

  // Calculator State
  const [calcDeptA, setCalcDeptA] = useState('ENGINEERING');
  const [calcWorkA, setCalcWorkA] = useState('TAMPING');
  const [calcDeptB, setCalcDeptB] = useState('SIGNALLING');
  const [calcWorkB, setCalcWorkB] = useState('POINT_MACHINE');
  const [calcResult, setCalcResult] = useState<any>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  useEffect(() => {
    fetchRulesAndFixtures();
  }, []);

  const fetchRulesAndFixtures = async () => {
    setIsLoading(true);
    try {
      const [rRes, fRes] = await Promise.all([
        fetch('http://127.0.0.1:8000/api/v1/rules'),
        fetch('http://127.0.0.1:8000/api/v1/packages/fixtures'),
      ]);
      if (rRes.ok) setRules(await rRes.json());
      if (fRes.ok) setFixtures(await fRes.json());
    } catch (e) {
      console.error('Failed to load rules/fixtures', e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRule) return;

    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/rules/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rule_id: selectedRule.rule_id,
          new_effect: verifyEffect,
          evidence_document: verifyEvidence,
          notes: verifyNotes,
          approving_officer: verifyOfficer,
        }),
      });

      if (res.ok) {
        setVerifySuccess(`Rule ${selectedRule.rule_id} verified successfully. New approved revision created.`);
        await fetchRulesAndFixtures();
        setTimeout(() => {
          setSelectedRule(null);
          setVerifySuccess(null);
        }, 2000);
      }
    } catch (err) {
      console.error('Verify failed', err);
    }
  };

  const handleCalculateCompatibility = async () => {
    setIsCalculating(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/rules/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          department_a: calcDeptA,
          work_type_a: calcWorkA,
          department_b: calcDeptB,
          work_type_b: calcWorkB,
        }),
      });
      if (res.ok) {
        setCalcResult(await res.json());
      }
    } catch (err) {
      console.error('Evaluation failed', err);
    } finally {
      setIsCalculating(false);
    }
  };

  const filteredRules = rules.filter((r) => {
    if (filterEffect === 'ALL') return true;
    return r.effect === filterEffect;
  });

  const getEffectBadge = (effect: string) => {
    switch (effect) {
      case 'ALLOWED':
        return (
          <span style={{ padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700, backgroundColor: 'var(--color-success-pale)', color: 'var(--color-success)', border: '1px solid var(--color-success)' }}>
            ALLOWED
          </span>
        );
      case 'PROHIBITED':
        return (
          <span style={{ padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700, backgroundColor: 'var(--color-danger-pale)', color: 'var(--color-danger)', border: '1px solid var(--color-danger)' }}>
            PROHIBITED
          </span>
        );
      case 'UNKNOWN':
      default:
        return (
          <span style={{ padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 700, backgroundColor: 'var(--color-warning-pale)', color: 'var(--color-warning)', border: '1px solid var(--color-warning)' }}>
            UNKNOWN (BLOCKS)
          </span>
        );
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* Top Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: 'var(--color-surface)',
          padding: '16px 20px',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--color-border)',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-ink)' }}>
              Rules, Compatibility & Executable Work Packages
            </h1>
            <ProvenanceBadge mode="TEST" />
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-muted)', marginTop: '2px' }}>
            Multi-department declarative compatibility rules, readiness oracle, and Phase DAG recipes (Phase 05)
          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setActiveTab('rules')}
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              fontWeight: 600,
              borderRadius: 'var(--radius-sm)',
              border: activeTab === 'rules' ? '1px solid var(--color-action)' : '1px solid var(--color-border)',
              backgroundColor: activeTab === 'rules' ? 'var(--color-surface-warm)' : 'var(--color-surface)',
              color: activeTab === 'rules' ? 'var(--color-action)' : 'var(--color-ink)',
              cursor: 'pointer',
            }}
          >
            Rules Registry ({isLoading ? '...' : rules.length})
          </button>
          <button
            onClick={() => setActiveTab('calculator')}
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              fontWeight: 600,
              borderRadius: 'var(--radius-sm)',
              border: activeTab === 'calculator' ? '1px solid var(--color-action)' : '1px solid var(--color-border)',
              backgroundColor: activeTab === 'calculator' ? 'var(--color-surface-warm)' : 'var(--color-surface)',
              color: activeTab === 'calculator' ? 'var(--color-action)' : 'var(--color-ink)',
              cursor: 'pointer',
            }}
          >
            Pairwise Evaluator
          </button>
          <button
            onClick={() => setActiveTab('fixtures')}
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              fontWeight: 600,
              borderRadius: 'var(--radius-sm)',
              border: activeTab === 'fixtures' ? '1px solid var(--color-action)' : '1px solid var(--color-border)',
              backgroundColor: activeTab === 'fixtures' ? 'var(--color-surface-warm)' : 'var(--color-surface)',
              color: activeTab === 'fixtures' ? 'var(--color-action)' : 'var(--color-ink)',
              cursor: 'pointer',
            }}
          >
            Canonical Benchmarks (3)
          </button>
        </div>
      </div>

      {/* Tab 1: Declarative Rules Registry */}
      {activeTab === 'rules' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Filter Bar */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: 'var(--color-surface)', padding: '10px 16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-ink)' }}>
              Declarative Safety & Compatibility Rules
            </div>
            <div style={{ display: 'flex', gap: '6px' }}>
              {['ALL', 'ALLOWED', 'PROHIBITED', 'UNKNOWN'].map((f) => (
                <button
                  key={f}
                  onClick={() => setFilterEffect(f)}
                  style={{
                    padding: '4px 10px',
                    fontSize: '11px',
                    fontWeight: filterEffect === f ? 700 : 500,
                    borderRadius: '4px',
                    border: '1px solid var(--color-border)',
                    backgroundColor: filterEffect === f ? 'var(--color-ink)' : 'var(--color-surface)',
                    color: filterEffect === f ? '#fff' : 'var(--color-muted)',
                    cursor: 'pointer',
                  }}
                >
                  {f}
                </button>
              ))}
            </div>
          </div>

          {/* Rules List */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {filteredRules.map((rule) => (
              <div
                key={rule.rule_id}
                style={{
                  backgroundColor: 'var(--color-surface)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--color-border)',
                  padding: '16px 20px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                }}
              >
                <div style={{ maxWidth: '82%' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '13px', fontWeight: 700, color: 'var(--color-action)' }}>
                      {rule.rule_id}
                    </span>
                    <span style={{ fontSize: '11px', color: 'var(--color-muted)', backgroundColor: 'var(--color-surface-warm)', padding: '2px 6px', borderRadius: '3px' }}>
                      Rev {rule.revision}
                    </span>
                    {getEffectBadge(rule.effect)}
                    <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-ink)' }}>
                      {rule.department_a} ({rule.work_type_a}) ⟷ {rule.department_b} ({rule.work_type_b})
                    </span>
                  </div>

                  <p style={{ fontSize: '13px', color: 'var(--color-ink)', lineHeight: 1.5, margin: '6px 0' }}>
                    {rule.description}
                  </p>

                  <div style={{ display: 'flex', gap: '16px', fontSize: '11px', color: 'var(--color-muted)', marginTop: '8px' }}>
                    <div>
                      Authority Ref: <strong style={{ color: 'var(--color-ink)', fontFamily: 'var(--font-mono)' }}>{rule.evidence_reference}</strong>
                    </div>
                    <div>
                      Author: <span style={{ color: 'var(--color-ink)' }}>{rule.author}</span>
                    </div>
                    <div>
                      Approver: <span style={{ color: 'var(--color-ink)' }}>{rule.approver}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <button
                    onClick={() => {
                      setSelectedRule(rule);
                      setVerifyEffect(rule.effect);
                      setVerifyEvidence(rule.evidence_reference);
                      setVerifyNotes('');
                    }}
                    style={{
                      padding: '6px 12px',
                      fontSize: '11px',
                      fontWeight: 600,
                      backgroundColor: 'var(--color-surface)',
                      border: '1px solid var(--color-action)',
                      color: 'var(--color-action)',
                      borderRadius: 'var(--radius-sm)',
                      cursor: 'pointer',
                    }}
                  >
                    Verify / Update
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Interactive Pairwise Calculator */}
      {activeTab === 'calculator' && (
        <div style={{ backgroundColor: 'var(--color-surface)', padding: '24px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--color-ink)', marginBottom: '4px' }}>
            Interactive Pairwise Compatibility Oracle
          </h2>
          <p style={{ fontSize: '12px', color: 'var(--color-muted)', marginBottom: '20px' }}>
            Tests whether two tasks from different departments can safely co-occupy a traffic possession. Evaluated against declarative IR rules where PROHIBITED strictly dominates ALLOWED.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            {/* Dept A */}
            <div style={{ padding: '16px', backgroundColor: 'var(--color-surface-warm)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-action)', marginBottom: '10px' }}>
                Primary Work (Department A)
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--color-muted)', display: 'block', marginBottom: '4px' }}>Department</label>
                  <select
                    value={calcDeptA}
                    onChange={(e) => setCalcDeptA(e.target.value)}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', backgroundColor: '#fff' }}
                  >
                    <option value="ENGINEERING">ENGINEERING (P-Way / TMS)</option>
                    <option value="SIGNALLING">SIGNALLING (S&T / SMMS)</option>
                    <option value="ELECTRICAL">ELECTRICAL (TRD / TDMS)</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--color-muted)', display: 'block', marginBottom: '4px' }}>Work Type Pattern</label>
                  <input
                    type="text"
                    value={calcWorkA}
                    onChange={(e) => setCalcWorkA(e.target.value)}
                    placeholder="e.g. TAMPING, BCM_DEEP_SCREENING, RAIL_GRINDING"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)' }}
                  />
                </div>
              </div>
            </div>

            {/* Dept B */}
            <div style={{ padding: '16px', backgroundColor: 'var(--color-surface-warm)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--color-action)', marginBottom: '10px' }}>
                Candidate Shadow Work (Department B)
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--color-muted)', display: 'block', marginBottom: '4px' }}>Department</label>
                  <select
                    value={calcDeptB}
                    onChange={(e) => setCalcDeptB(e.target.value)}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', backgroundColor: '#fff' }}
                  >
                    <option value="SIGNALLING">SIGNALLING (S&T / SMMS)</option>
                    <option value="ENGINEERING">ENGINEERING (P-Way / TMS)</option>
                    <option value="ELECTRICAL">ELECTRICAL (TRD / TDMS)</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '11px', color: 'var(--color-muted)', display: 'block', marginBottom: '4px' }}>Work Type Pattern</label>
                  <input
                    type="text"
                    value={calcWorkB}
                    onChange={(e) => setCalcWorkB(e.target.value)}
                    placeholder="e.g. POINT_MACHINE, AXLE_COUNTER, OHE_INSPECTION"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)' }}
                  />
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={handleCalculateCompatibility}
            disabled={isCalculating}
            style={{
              padding: '10px 24px',
              backgroundColor: 'var(--color-action)',
              color: '#fff',
              border: 'none',
              borderRadius: 'var(--radius-sm)',
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              marginBottom: '20px',
            }}
          >
            {isCalculating ? 'Evaluating Precedence Rules...' : 'Run Compatibility Evaluation'}
          </button>

          {/* Result Box */}
          {calcResult && (
            <div
              style={{
                padding: '20px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)',
                backgroundColor:
                  calcResult.effect === 'ALLOWED'
                    ? 'var(--color-success-pale)'
                    : calcResult.effect === 'PROHIBITED'
                    ? 'var(--color-danger-pale)'
                    : 'var(--color-warning-pale)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--color-ink)' }}>
                  Evaluation Verdict:
                </span>
                {getEffectBadge(calcResult.effect)}
                {calcResult.dominant_rule && (
                  <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--color-ink)' }}>
                    Governing Rule: {calcResult.dominant_rule}
                  </span>
                )}
              </div>
              <p style={{ fontSize: '13px', color: 'var(--color-ink)', lineHeight: 1.5, margin: 0 }}>
                {calcResult.explanation}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Canonical Demonstration Benchmarks (Blueprint Section 18) */}
      {activeTab === 'fixtures' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ backgroundColor: 'var(--color-surface)', padding: '16px 20px', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 700, color: 'var(--color-ink)', marginBottom: '4px' }}>
              Hand-Checkable Benchmark Work Packages (Blueprint Section 18)
            </h2>
            <p style={{ fontSize: '12px', color: 'var(--color-muted)', margin: 0 }}>
              Three explicit reference scenarios verified in automated unit and integration tests.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {fixtures.map((pkg, idx) => (
              <div
                key={pkg.package_id}
                style={{
                  backgroundColor: 'var(--color-surface)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--color-border)',
                  padding: '20px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <span style={{ fontSize: '14px', fontWeight: 700, color: 'var(--color-ink)' }}>
                        Case {idx + 1}: {pkg.recipe.name}
                      </span>
                      <span style={{ padding: '2px 6px', backgroundColor: 'var(--color-surface-warm)', fontSize: '11px', fontFamily: 'var(--font-mono)', borderRadius: '3px' }}>
                        {pkg.recipe.assumption_badge}
                      </span>
                      {pkg.is_eligible ? (
                        <span style={{ padding: '2px 8px', backgroundColor: 'var(--color-success-pale)', color: 'var(--color-success)', fontSize: '11px', fontWeight: 700, borderRadius: '4px' }}>
                          ELIGIBLE ({pkg.recipe.total_duration_minutes} MINS)
                        </span>
                      ) : (
                        <span style={{ padding: '2px 8px', backgroundColor: 'var(--color-danger-pale)', color: 'var(--color-danger)', fontSize: '11px', fontWeight: 700, borderRadius: '4px' }}>
                          INELIGIBLE / REJECTED
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--color-muted)' }}>
                      Tasks: <strong style={{ color: 'var(--color-ink)' }}>{pkg.business_keys.join(' + ')}</strong> | Track: <span style={{ fontFamily: 'var(--font-mono)' }}>{pkg.track_segment_id}</span> | Capacity Demand: <strong>{pkg.cumulative_capacity_required} / {pkg.available_capacity} units</strong>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '18px', fontWeight: 700, color: pkg.is_eligible ? 'var(--color-action)' : 'var(--color-danger)' }}>
                      {pkg.is_eligible ? `${pkg.recipe.total_duration_minutes}m` : 'BLOCKED'}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--color-muted)' }}>Total Block Duration</div>
                  </div>
                </div>

                {pkg.ineligibility_reason && (
                  <div style={{ padding: '10px 14px', backgroundColor: 'var(--color-danger-pale)', color: 'var(--color-danger)', borderRadius: 'var(--radius-sm)', fontSize: '12px', marginBottom: '14px', border: '1px solid var(--color-danger)' }}>
                    <strong>Rejection Reason:</strong> {pkg.ineligibility_reason}
                  </div>
                )}

                {/* Phase DAG timeline */}
                <div style={{ marginTop: '12px' }}>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                    Materialized Phase DAG Breakdown
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '8px' }}>
                    {pkg.recipe.phases.map((ph, pi) => (
                      <div
                        key={pi}
                        style={{
                          padding: '10px',
                          backgroundColor: 'var(--color-surface-warm)',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--color-border)',
                          fontSize: '12px',
                        }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600, color: 'var(--color-action)' }}>
                          <span>{ph.phase_type}</span>
                          <span>{ph.duration_minutes}m</span>
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>
                          Offset: [{ph.offset_start_minutes}m ➔ {ph.offset_end_minutes}m]
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--color-ink)', marginTop: '4px', lineHeight: 1.3 }}>
                          {ph.description}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Verify / Update Modal */}
      {selectedRule && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.4)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 100,
          }}
        >
          <div
            style={{
              backgroundColor: '#fff',
              borderRadius: 'var(--radius-lg)',
              padding: '24px',
              width: '500px',
              maxWidth: '90%',
              boxShadow: 'var(--shadow-lg)',
              border: '1px solid var(--color-border)',
            }}
          >
            <h2 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--color-ink)', marginBottom: '4px' }}>
              Formal Rule Verification: {selectedRule.rule_id}
            </h2>
            <p style={{ fontSize: '12px', color: 'var(--color-muted)', marginBottom: '16px' }}>
              Per blueprint invariant, verification creates a new approved rule revision with attached evidence; it never uses an unverified bypass flag.
            </p>

            {verifySuccess ? (
              <div style={{ padding: '16px', backgroundColor: 'var(--color-success-pale)', color: 'var(--color-success)', borderRadius: 'var(--radius-sm)', fontSize: '13px', fontWeight: 600 }}>
                {verifySuccess}
              </div>
            ) : (
              <form onSubmit={handleVerifySubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Effect Decision</label>
                  <select
                    value={verifyEffect}
                    onChange={(e: any) => setVerifyEffect(e.target.value)}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)' }}
                  >
                    <option value="ALLOWED">ALLOWED</option>
                    <option value="PROHIBITED">PROHIBITED</option>
                    <option value="UNKNOWN">UNKNOWN</option>
                  </select>
                </div>

                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Documentary Evidence Citation</label>
                  <input
                    type="text"
                    value={verifyEvidence}
                    onChange={(e) => setVerifyEvidence(e.target.value)}
                    placeholder="e.g. JOINT_SAFETY_CIRCULAR_JSC_2026_09"
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)' }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Engineering Review Comments</label>
                  <textarea
                    value={verifyNotes}
                    onChange={(e) => setVerifyNotes(e.target.value)}
                    placeholder="Detail reasons, test conditions, or safety equipment used"
                    required
                    rows={3}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)' }}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '12px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Approving Authority</label>
                  <input
                    type="text"
                    value={verifyOfficer}
                    onChange={(e) => setVerifyOfficer(e.target.value)}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)' }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '10px' }}>
                  <button
                    type="button"
                    onClick={() => setSelectedRule(null)}
                    style={{ padding: '8px 16px', backgroundColor: 'var(--color-surface-warm)', border: '1px solid var(--color-border)', borderRadius: '4px', fontSize: '12px', cursor: 'pointer' }}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    style={{ padding: '8px 16px', backgroundColor: 'var(--color-action)', color: '#fff', border: 'none', borderRadius: '4px', fontSize: '12px', fontWeight: 600, cursor: 'pointer' }}
                  >
                    Authorize & Create Revision
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
