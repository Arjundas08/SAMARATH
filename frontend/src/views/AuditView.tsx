import React from 'react';
import { Shield } from 'lucide-react';

export const AuditView: React.FC = () => {
  const auditEntries = [
    {
      time: '2026-10-11T18:00:00Z',
      action: 'SNAPSHOT_SEALED',
      user: 'operator_ingest',
      entity: 'c3d5f8a1-2b4e-4f7c-9a1d-8e6b3c2a1f0e',
      detail: 'Sealed immutable input snapshot for Corridor VKC Week 42 (60 Demands, 280 Trains).',
    },
    {
      time: '2026-10-11T18:05:08Z',
      action: 'INDEPENDENT_CHECK_PASSED',
      user: 'feasibility_checker_oracle',
      entity: 'val-98765432-10fe-dcba',
      detail: 'Independent Checker verified zero track collisions and valid power block isolation.',
    },
    {
      time: '2026-10-11T19:30:00Z',
      action: 'PROGRAMME_APPROVED',
      user: 'approver_operating (Arun Kumar)',
      entity: 'plan-vkc-2026-w42-v1',
      detail: 'Operational block programme ratified under delegated Senior DOM operating authority.',
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
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
          <h1 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-ink)' }}>
            Immutable Audit Trail & Decision Ledger
          </h1>
          <div style={{ fontSize: '12px', color: 'var(--color-muted)', marginTop: '2px' }}>
            Append-only transactional log recording all snapshot sealings, solver runs, and approvals
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--color-success)', fontWeight: 600 }}>
          <Shield size={16} />
          <span>Ledger Integrity Verified</span>
        </div>
      </div>

      <div
        style={{
          backgroundColor: 'var(--color-surface)',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--color-border)',
          overflow: 'hidden',
        }}
      >
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', textAlign: 'left' }}>
          <thead>
            <tr style={{ backgroundColor: 'var(--color-surface-warm)', borderBottom: '1px solid var(--color-border)', color: 'var(--color-muted)', fontSize: '11px', textTransform: 'uppercase' }}>
              <th style={{ padding: '12px 16px' }}>Timestamp (IST)</th>
              <th style={{ padding: '12px 16px' }}>Action</th>
              <th style={{ padding: '12px 16px' }}>Operator / Role</th>
              <th style={{ padding: '12px 16px' }}>Target Entity ID</th>
              <th style={{ padding: '12px 16px' }}>Audit Details</th>
            </tr>
          </thead>
          <tbody>
            {auditEntries.map((e, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
                <td style={{ padding: '12px 16px', fontSize: '12px', color: 'var(--color-muted)' }}>
                  {new Date(e.time).toLocaleString('en-IN', { timeZone: 'Asia/Kolkata' })}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <code style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-action)' }}>
                    {e.action}
                  </code>
                </td>
                <td style={{ padding: '12px 16px', fontWeight: 600 }}>{e.user}</td>
                <td style={{ padding: '12px 16px', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--color-muted)' }}>
                  {e.entity}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '12px' }}>{e.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
