import React from 'react';
import { ProvenanceMode } from '../../types/api';

interface ProvenanceBadgeProps {
  mode: ProvenanceMode;
  size?: 'sm' | 'md';
}

export const ProvenanceBadge: React.FC<ProvenanceBadgeProps> = ({ mode, size = 'sm' }) => {
  const configs = {
    TEST: {
      label: '[TEST MODE]',
      bg: 'var(--color-warning-pale)',
      text: 'var(--color-warning)',
      border: 'var(--color-warning)',
      desc: 'Synthetic demonstration corridor data',
    },
    SYNTHETIC_SCENARIO: {
      label: '[SCENARIO]',
      bg: 'var(--color-change-pale)',
      text: 'var(--color-change)',
      border: 'var(--color-change)',
      desc: 'Evaluator stress challenge scenario',
    },
    AUTHORIZED_IMPORT: {
      label: '[AUTHORIZED]',
      bg: 'var(--color-success-pale)',
      text: 'var(--color-success)',
      border: 'var(--color-success)',
      desc: 'Formally ingested from approved export',
    },
  };

  const c = configs[mode] || configs.TEST;
  const padding = size === 'sm' ? '2px 6px' : '4px 10px';
  const fontSize = size === 'sm' ? '10px' : '12px';

  return (
    <span
      title={c.desc}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding,
        fontSize,
        fontWeight: 700,
        letterSpacing: '0.5px',
        backgroundColor: c.bg,
        color: c.text,
        border: `1px solid ${c.border}`,
        borderRadius: 'var(--radius-sm)',
        userSelect: 'none',
      }}
    >
      {c.label}
    </span>
  );
};
