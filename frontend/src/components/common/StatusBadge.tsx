import React from 'react';

type StatusType =
  | 'APPROVED_PROGRAMME'
  | 'DRAFT_PROPOSAL'
  | 'CHECKED_FEASIBLE'
  | 'STALE'
  | 'PASS'
  | 'FAIL'
  | 'UNKNOWN'
  | 'TIER_1_MANDATORY'
  | 'TIER_2_SPEED_RESTRICTION'
  | 'TIER_3_CYCLIC'
  | 'LOCKED';

interface StatusBadgeProps {
  status: StatusType | string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getStyle = (): { bg: string; text: string; border: string; label: string } => {
    switch (status) {
      case 'APPROVED_PROGRAMME':
        return { bg: 'var(--color-success-pale)', text: 'var(--color-success)', border: 'var(--color-success)', label: 'Approved Programme' };
      case 'CHECKED_FEASIBLE':
        return { bg: 'var(--color-action-tint)', text: 'var(--color-action)', border: 'var(--color-action)', label: 'Checked Feasible' };
      case 'DRAFT_PROPOSAL':
        return { bg: '#F1F5F9', text: '#475569', border: '#CBD5E1', label: 'Draft Proposal' };
      case 'STALE':
        return { bg: 'var(--color-change-pale)', text: 'var(--color-change)', border: 'var(--color-change)', label: 'Stale / Superseded' };
      case 'PASS':
        return { bg: 'var(--color-success-pale)', text: 'var(--color-success)', border: 'var(--color-success)', label: 'PASS' };
      case 'FAIL':
        return { bg: 'var(--color-critical-pale)', text: 'var(--color-critical)', border: 'var(--color-critical)', label: 'FAIL' };
      case 'UNKNOWN':
        return { bg: 'var(--color-warning-pale)', text: 'var(--color-warning)', border: 'var(--color-warning)', label: 'UNKNOWN (Blocked)' };
      case 'TIER_1_MANDATORY':
        return { bg: 'var(--color-critical-pale)', text: 'var(--color-critical)', border: 'var(--color-critical)', label: 'Tier 1: Mandatory' };
      case 'TIER_2_SPEED_RESTRICTION':
        return { bg: 'var(--color-warning-pale)', text: 'var(--color-warning)', border: 'var(--color-warning)', label: 'Tier 2: Speed Restriction' };
      case 'TIER_3_CYCLIC':
        return { bg: '#F1F5F9', text: '#475569', border: '#CBD5E1', label: 'Tier 3: Cyclic' };
      case 'LOCKED':
        return { bg: '#EFF6FF', text: '#1D4ED8', border: '#93C5FD', label: 'Locked Commitment' };
      default:
        return { bg: '#F1F5F9', text: '#475569', border: '#CBD5E1', label: status };
    }
  };

  const s = getStyle();

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        fontSize: '11px',
        fontWeight: 600,
        backgroundColor: s.bg,
        color: s.text,
        border: `1px solid ${s.border}`,
        borderRadius: 'var(--radius-sm)',
        whiteSpace: 'nowrap',
      }}
    >
      {s.label}
    </span>
  );
};
