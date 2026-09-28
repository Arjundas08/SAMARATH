import React from 'react';
import { LucideIcon } from 'lucide-react';

interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  prerequisiteNote?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon,
  title,
  description,
  actionLabel,
  onAction,
  prerequisiteNote,
}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '48px 24px',
        backgroundColor: 'var(--color-surface)',
        borderRadius: 'var(--radius-lg)',
        border: '1px dashed var(--color-border)',
        textAlign: 'center',
        maxWidth: '560px',
        margin: '32px auto',
      }}
    >
      <div
        style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          backgroundColor: 'var(--color-action-tint)',
          color: 'var(--color-action)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '16px',
        }}
      >
        <Icon size={24} />
      </div>

      <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--color-ink)', marginBottom: '8px' }}>
        {title}
      </h3>

      <p style={{ fontSize: '13px', color: 'var(--color-muted)', lineHeight: 1.6, marginBottom: '20px' }}>
        {description}
      </p>

      {prerequisiteNote && (
        <div
          style={{
            fontSize: '11px',
            color: 'var(--color-warning)',
            backgroundColor: 'var(--color-warning-pale)',
            border: '1px solid var(--color-warning)',
            padding: '6px 12px',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '16px',
          }}
        >
          <strong>Prerequisite:</strong> {prerequisiteNote}
        </div>
      )}

      {actionLabel && onAction && (
        <button
          onClick={onAction}
          style={{
            padding: '8px 18px',
            backgroundColor: 'var(--color-action)',
            color: '#FFFFFF',
            border: 'none',
            borderRadius: 'var(--radius-md)',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'background-color 0.15s ease',
          }}
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
};
