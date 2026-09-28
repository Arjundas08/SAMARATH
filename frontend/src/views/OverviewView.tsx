import React from 'react';
import { Calendar } from 'lucide-react';
import { EmptyState } from '../components/common/EmptyState';
import { ProvenanceBadge } from '../components/common/ProvenanceBadge';

interface OverviewViewProps {
  onNavigateToPlanning?: () => void;
  onNavigateToMaintenance?: () => void;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  onNavigateToPlanning,
  onNavigateToMaintenance,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Banner */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px',
          backgroundColor: 'var(--color-surface)',
          padding: '20px 24px',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--color-border)',
        }}
      >
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-ink)' }}>
              Operational Briefing — Corridor Vayu-Kosh (VKC)
            </h1>
            <ProvenanceBadge mode="TEST" />
          </div>
          <p style={{ fontSize: '13px', color: 'var(--color-muted)', marginTop: '4px' }}>
            Territory Scope: Division HQ | Weekly Planning Window: 12-18 Oct 2026 (IST)
          </p>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={onNavigateToMaintenance}
            style={{
              padding: '6px 14px',
              backgroundColor: 'var(--color-surface-warm)',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-md)',
              fontSize: '12px',
              fontWeight: 600,
            }}
          >
            Review Demands
          </button>
          <button
            onClick={onNavigateToPlanning}
            style={{
              padding: '6px 14px',
              backgroundColor: 'var(--color-action)',
              color: '#FFFFFF',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              fontSize: '12px',
              fontWeight: 600,
            }}
          >
            Open Planning Canvas
          </button>
        </div>
      </div>

      {/* Corridor Key Facts Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Track Geometry</div>
          <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>120.0 Km</div>
          <div style={{ fontSize: '12px', color: 'var(--color-muted)', marginTop: '2px' }}>Double Track (UP & DOWN)</div>
        </div>

        <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Stations / Blocks</div>
          <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>6 Stations</div>
          <div style={{ fontSize: '12px', color: 'var(--color-muted)', marginTop: '2px' }}>10 Directional Block Sections</div>
        </div>

        <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Traction Power</div>
          <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>25 kV AC</div>
          <div style={{ fontSize: '12px', color: 'var(--color-muted)', marginTop: '2px' }}>3 TSS + 1 Neutral Section (SP-1)</div>
        </div>

        <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', textTransform: 'uppercase', fontWeight: 600 }}>Demonstration Scope</div>
          <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>60 M / 30 W</div>
          <div style={{ fontSize: '12px', color: 'var(--color-muted)', marginTop: '2px' }}>Monthly tasks / Weekly detailed slice</div>
        </div>
      </div>

      {/* Honest Empty State for Initial Solver Run */}
      <EmptyState
        icon={Calendar}
        title="No Operational Plan Materialized for Active Horizon"
        description="The system has not yet generated a reconciled weekly schedule for Week 42. Ingest departmental demands or seed the corridor dataset to generate the first candidate plan."
        prerequisiteNote="Requires sealed Snapshot containing TMS, SMMS, and TDMS demands."
        actionLabel="Go to Maintenance Queue"
        onAction={onNavigateToMaintenance}
      />
    </div>
  );
};
