import React, { useState } from 'react';
import {
  ProvenanceBadge,
} from '../components/common/ProvenanceBadge';
import { StatusBadge } from '../components/common/StatusBadge';
import { ErrorSummary } from '../components/common/ErrorSummary';
import { PhaseSequence } from '../components/common/PhaseSequence';
import { EvidenceDrawer } from '../components/common/EvidenceDrawer';
import { AlertCircle, ShieldAlert, Lock, ServerOff } from 'lucide-react';
import { Task } from '../types/api';

export const ComponentGalleryView: React.FC = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);

  const fixtureTask: Task = {
    task_id: 'fix-task-999',
    business_key: 'TASK-TMS-0099-DEEP-SCREENING-LONG-KEY',
    department: 'ENGINEERING',
    sub_department: 'PERMANENT_WAY_CIVIL',
    work_type: 'DEEP_SCREENING_BCM',
    description: 'Extensive mechanized ballast cleaning with high-capacity Ballast Cleaning Machine (BCM-01) on continuous welded rail (CWR) section with associated OHE power de-energization.',
    station_from: 'ALPHA_JUNCTION',
    station_to: 'BRAVO_MAIN',
    track_segment_id: 'SEC-01-UP-MAIN',
    chainage_start_km: 12.345,
    chainage_end_km: 16.789,
    duration_minutes: 240,
    setup_buffer_minutes: 30,
    restoration_buffer_minutes: 30,
    total_block_minutes: 300,
    criticality: 'TIER_1_MANDATORY',
    deadline_utc: '2026-10-18T23:59:59Z',
    preferred_windows: [
      { window_start_utc: '2026-10-14T01:00:00Z', window_end_utc: '2026-10-14T07:00:00Z' }
    ],
    required_resources: [
      { resource_type: 'MACHINE', resource_id: 'BCM-HEAVY-DUTY-01', quantity: 1 },
      { resource_type: 'CREW', resource_id: 'GANG-PWAY-SPECIALIZED-A', quantity: 1 }
    ],
    requires_power_block: true,
    power_block_elementary_section: 'ES-ALP-BRV-TRACK-SECTION-01',
    requires_speed_restriction_after: true,
    imposed_speed_kmh: 45,
    demand_status: 'VALIDATED',
    provenance_mode: 'TEST',
    created_at_utc: '2026-10-01T10:00:00Z',
    created_by: 'planner_tms',
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', paddingBottom: '60px' }}>
      {/* Prominent UI Fixture Header */}
      <div
        style={{
          padding: '12px 16px',
          backgroundColor: '#EFF6FF',
          border: '1px solid #3B82F6',
          borderRadius: 'var(--radius-md)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <div>
          <strong style={{ color: '#1D4ED8', fontSize: '13px' }}>
            [DEVELOPMENT ONLY — UI FIXTURE & COMPONENT GALLERY]
          </strong>
          <div style={{ fontSize: '11px', color: '#3B82F6', marginTop: '2px' }}>
            Isolated component preview. Fixtures verify layout, typography, contrast, and edge states.
          </div>
        </div>
        <button
          onClick={() => setDrawerOpen(true)}
          style={{
            padding: '6px 14px',
            backgroundColor: '#2563EB',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          Open Fixture Evidence Drawer
        </button>
      </div>

      {/* 1. Badges & Semantics */}
      <section style={{ backgroundColor: '#FFFFFF', padding: '20px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
        <h2 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>1. Data Provenance & Semantic Status Badges</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center' }}>
          <ProvenanceBadge mode="TEST" />
          <ProvenanceBadge mode="SYNTHETIC_SCENARIO" />
          <ProvenanceBadge mode="AUTHORIZED_IMPORT" />
          <StatusBadge status="APPROVED_PROGRAMME" />
          <StatusBadge status="CHECKED_FEASIBLE" />
          <StatusBadge status="DRAFT_PROPOSAL" />
          <StatusBadge status="STALE" />
          <StatusBadge status="PASS" />
          <StatusBadge status="FAIL" />
          <StatusBadge status="UNKNOWN" />
          <StatusBadge status="TIER_1_MANDATORY" />
          <StatusBadge status="TIER_2_SPEED_RESTRICTION" />
          <StatusBadge status="TIER_3_CYCLIC" />
          <StatusBadge status="LOCKED" />
        </div>
      </section>

      {/* 2. Phase Sequence */}
      <section style={{ backgroundColor: '#FFFFFF', padding: '20px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
        <h2 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>2. Phase Sequence Timeline Representation</h2>
        <div style={{ maxWidth: '600px' }}>
          <PhaseSequence setupMinutes={30} workMinutes={240} restorationMinutes={30} />
        </div>
      </section>

      {/* 3. RFC 7807 Error Summary */}
      <section style={{ backgroundColor: '#FFFFFF', padding: '20px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
        <h2 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>3. RFC 7807 Typed Error Presentation</h2>
        <ErrorSummary
          error={{
            type: 'https://samarath.railnet.gov.in/errors/resource-conflict',
            title: 'Unresolvable Hard Resource Conflict',
            status: 409,
            detail: 'Requested task TASK-TMS-0015 conflicts with locked commitment TASK-TMS-0008 on machine BCM-01.',
            error_code: 'ERR_RESOURCE_LOCKED',
            invalid_params: [
              { name: 'required_resources[0].resource_id', reason: 'BCM-01 is under locked possession from 01:00 to 05:00 UTC.' }
            ],
          }}
        />
      </section>

      {/* 4. States Gallery: Empty, Infeasible, Stale, Permission-Denied, Service-Unavailable */}
      <section style={{ backgroundColor: '#FFFFFF', padding: '20px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
        <h2 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '16px' }}>4. State Quality Showcase</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '16px' }}>
          {/* Permission Denied */}
          <div style={{ padding: '16px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--color-surface-warm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-critical)', fontWeight: 700, fontSize: '13px', marginBottom: '6px' }}>
              <Lock size={16} />
              <span>Permission Denied (403)</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--color-ink)' }}>
              Action requires 'PROGRAMME_APPROVE' authority. Infrastructure Administrator role is prohibited from approving programmes.
            </p>
          </div>

          {/* Stale Plan */}
          <div style={{ padding: '16px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--color-surface-warm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-warning)', fontWeight: 700, fontSize: '13px', marginBottom: '6px' }}>
              <AlertCircle size={16} />
              <span>Plan Stale (Disrupted Input)</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--color-ink)' }}>
              Train 12002 was delayed by +45 mins, intersecting block TASK-TMS-0012. Replan required.
            </p>
          </div>

          {/* Infeasible Input */}
          <div style={{ padding: '16px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--color-surface-warm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-critical)', fontWeight: 700, fontSize: '13px', marginBottom: '6px' }}>
              <ShieldAlert size={16} />
              <span>Infeasible Formulation</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--color-ink)' }}>
              Mandatory work exceeds total available track window between scheduled Rajdhani paths.
            </p>
          </div>

          {/* Service Unavailable */}
          <div style={{ padding: '16px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--color-surface-warm)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-muted)', fontWeight: 700, fontSize: '13px', marginBottom: '6px' }}>
              <ServerOff size={16} />
              <span>Database Unavailable (Degraded)</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--color-ink)' }}>
              FastAPI process reachable, but PostgreSQL lease connection timed out.
            </p>
          </div>
        </div>
      </section>

      {/* Evidence Drawer Container */}
      <EvidenceDrawer
        task={fixtureTask}
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
};
