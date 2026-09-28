import React from 'react';
import { AlertCircle } from 'lucide-react';

export interface InvalidParamItem {
  name: string;
  reason: string;
}

export interface ProblemDetailsData {
  type: string;
  title: string;
  status: number;
  detail: string;
  error_code: string;
  invalid_params?: InvalidParamItem[];
}

interface ErrorSummaryProps {
  error: ProblemDetailsData | string;
  onDismiss?: () => void;
}

export const ErrorSummary: React.FC<ErrorSummaryProps> = ({ error, onDismiss }) => {
  if (typeof error === 'string') {
    return (
      <div
        style={{
          display: 'flex',
          gap: '12px',
          padding: '14px 16px',
          backgroundColor: 'var(--color-critical-pale)',
          borderLeft: '4px solid var(--color-critical)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--color-critical)',
          marginBottom: '16px',
        }}
      >
        <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
        <div style={{ flex: 1, fontSize: '13px' }}>{error}</div>
        {onDismiss && (
          <button onClick={onDismiss} style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}>
            ✕
          </button>
        )}
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        padding: '16px',
        backgroundColor: 'var(--color-critical-pale)',
        borderLeft: '4px solid var(--color-critical)',
        borderRadius: 'var(--radius-sm)',
        marginBottom: '16px',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-critical)', fontWeight: 700, fontSize: '14px' }}>
          <AlertCircle size={18} />
          <span>{error.title} ({error.error_code})</span>
        </div>
        {onDismiss && (
          <button onClick={onDismiss} style={{ background: 'none', border: 'none', color: 'var(--color-critical)', cursor: 'pointer' }}>
            ✕
          </button>
        )}
      </div>

      <p style={{ fontSize: '13px', color: 'var(--color-ink)', lineHeight: 1.5 }}>
        {error.detail}
      </p>

      {error.invalid_params && error.invalid_params.length > 0 && (
        <div style={{ marginTop: '8px', borderTop: '1px solid rgba(179,54,54,0.2)', paddingTop: '8px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-critical)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Validation Errors:
          </div>
          <ul style={{ paddingLeft: '20px', fontSize: '12px', color: 'var(--color-ink)' }}>
            {error.invalid_params.map((p, idx) => (
              <li key={idx} style={{ marginBottom: '2px' }}>
                <code style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{p.name}</code>: {p.reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
