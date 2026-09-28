import React from 'react';

interface PhaseSequenceProps {
  setupMinutes: number;
  workMinutes: number;
  restorationMinutes: number;
  showLabels?: boolean;
}

export const PhaseSequence: React.FC<PhaseSequenceProps> = ({
  setupMinutes,
  workMinutes,
  restorationMinutes,
  showLabels = true,
}) => {
  const total = setupMinutes + workMinutes + restorationMinutes;
  const setupPct = Math.max(5, (setupMinutes / total) * 100);
  const workPct = Math.max(10, (workMinutes / total) * 100);
  const restoPct = Math.max(5, (restorationMinutes / total) * 100);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', width: '100%' }}>
      <div
        style={{
          display: 'flex',
          height: '14px',
          borderRadius: 'var(--radius-sm)',
          overflow: 'hidden',
          backgroundColor: '#E2E8F0',
        }}
      >
        {/* Setup Phase */}
        <div
          title={`Setup: ${setupMinutes}m`}
          style={{
            width: `${setupPct}%`,
            backgroundColor: '#CBD5E1',
            borderRight: '1px solid #FFFFFF',
          }}
        />
        {/* Productive Work Phase */}
        <div
          title={`Productive Work: ${workMinutes}m`}
          style={{
            width: `${workPct}%`,
            backgroundColor: 'var(--color-action)',
            borderRight: '1px solid #FFFFFF',
          }}
        />
        {/* Restoration Phase */}
        <div
          title={`Restoration: ${restorationMinutes}m`}
          style={{
            width: `${restoPct}%`,
            backgroundColor: '#94A3B8',
          }}
        />
      </div>

      {showLabels && (
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--color-muted)' }}>
          <span>Setup: {setupMinutes}m</span>
          <span style={{ fontWeight: 600, color: 'var(--color-ink)' }}>Work: {workMinutes}m</span>
          <span>Restore: {restorationMinutes}m</span>
        </div>
      )}
    </div>
  );
};
