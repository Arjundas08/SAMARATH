import React, { useState, useMemo } from 'react';
import { MaterializedAssignment } from '../../types/api';
import { Search, Lock, Zap, CheckCircle2, Layers, ArrowUpDown } from 'lucide-react';

interface TabularScheduleViewProps {
  assignments: MaterializedAssignment[];
  selectedAssignment: MaterializedAssignment | null;
  onSelectAssignment: (assignment: MaterializedAssignment | null) => void;
}

export const TabularScheduleView: React.FC<TabularScheduleViewProps> = ({
  assignments,
  selectedAssignment,
  onSelectAssignment,
}) => {
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('ALL');
  const [sortField, setSortField] = useState<'start_minute' | 'duration_minutes' | 'business_key'>('start_minute');
  const [sortAsc, setSortAsc] = useState(true);

  // Format minute of week to Asia/Kolkata date & time
  const formatMinuteToIST = (minute: number): string => {
    const days = ['Mon 12 Oct', 'Tue 13 Oct', 'Wed 14 Oct', 'Thu 15 Oct', 'Fri 16 Oct', 'Sat 17 Oct', 'Sun 18 Oct'];
    const dayIdx = Math.min(6, Math.floor(minute / 1440));
    const dayMinute = minute % 1440;
    const hours = Math.floor(dayMinute / 60);
    const mins = dayMinute % 60;
    return `${days[dayIdx]} ${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
  };

  const filteredAssignments = useMemo(() => {
    let list = assignments.filter((a) => {
      if (deptFilter !== 'ALL') {
        if (!a.business_key.includes(deptFilter)) return false;
      }
      if (search.trim()) {
        const q = search.toLowerCase();
        return (
          a.business_key.toLowerCase().includes(q) ||
          a.track_segment_id.toLowerCase().includes(q) ||
          a.assignment_id.toLowerCase().includes(q)
        );
      }
      return true;
    });

    list.sort((a, b) => {
      const valA = a[sortField];
      const valB = b[sortField];
      if (valA < valB) return sortAsc ? -1 : 1;
      if (valA > valB) return sortAsc ? 1 : -1;
      return 0;
    });

    return list;
  }, [assignments, search, deptFilter, sortField, sortAsc]);

  const toggleSort = (field: 'start_minute' | 'duration_minutes' | 'business_key') => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(true);
    }
  };

  return (
    <div style={{ backgroundColor: '#FFFFFF', padding: '16px 20px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
      {/* Table Toolbar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <Search size={12} color="var(--color-muted)" style={{ position: 'absolute', left: '8px', top: '7px' }} />
            <input
              type="text"
              placeholder="Filter blocks by key or segment..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              style={{
                padding: '5px 8px 5px 24px',
                fontSize: '11px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border)',
                width: '220px',
              }}
            />
          </div>

          <select
            value={deptFilter}
            onChange={(e) => setDeptFilter(e.target.value)}
            style={{
              padding: '5px 8px',
              fontSize: '11px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-border)',
              backgroundColor: '#FFFFFF',
            }}
          >
            <option value="ALL">All Departments</option>
            <option value="ENG">Civil (ENG)</option>
            <option value="ELE">Electrical (ELE)</option>
            <option value="SIG">Signalling (SIG)</option>
          </select>
        </div>

        <div style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
          Showing <b>{filteredAssignments.length}</b> scheduled blocks
        </div>
      </div>

      {/* Accessible Table */}
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px', textAlign: 'left' }}>
          <thead>
            <tr style={{ backgroundColor: 'var(--color-surface-warm)', borderBottom: '1px solid var(--color-border)' }}>
              <th
                onClick={() => toggleSort('business_key')}
                style={{ padding: '8px 10px', fontWeight: 600, color: 'var(--color-ink)', cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span>Task Key</span>
                  <ArrowUpDown size={11} />
                </div>
              </th>
              <th style={{ padding: '8px 10px', fontWeight: 600, color: 'var(--color-ink)' }}>Track Segment</th>
              <th
                onClick={() => toggleSort('start_minute')}
                style={{ padding: '8px 10px', fontWeight: 600, color: 'var(--color-ink)', cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span>Window (Asia/Kolkata)</span>
                  <ArrowUpDown size={11} />
                </div>
              </th>
              <th
                onClick={() => toggleSort('duration_minutes')}
                style={{ padding: '8px 10px', fontWeight: 600, color: 'var(--color-ink)', cursor: 'pointer' }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span>Duration</span>
                  <ArrowUpDown size={11} />
                </div>
              </th>
              <th style={{ padding: '8px 10px', fontWeight: 600, color: 'var(--color-ink)' }}>Power Block</th>
              <th style={{ padding: '8px 10px', fontWeight: 600, color: 'var(--color-ink)' }}>Lock</th>
              <th style={{ padding: '8px 10px', fontWeight: 600, color: 'var(--color-ink)' }}>Type</th>
              <th style={{ padding: '8px 10px', fontWeight: 600, color: 'var(--color-ink)' }}>Oracle Verdict</th>
            </tr>
          </thead>
          <tbody>
            {filteredAssignments.map((a) => {
              const isSelected = selectedAssignment?.assignment_id === a.assignment_id;
              return (
                <tr
                  key={a.assignment_id}
                  onClick={() => onSelectAssignment(a)}
                  style={{
                    borderBottom: '1px solid var(--color-border-subtle)',
                    backgroundColor: isSelected ? 'var(--color-action-tint)' : '#FFFFFF',
                    cursor: 'pointer',
                    transition: 'background 0.15s ease',
                  }}
                >
                  <td style={{ padding: '8px 10px', fontWeight: 700, color: 'var(--color-ink)' }}>
                    {a.business_key}
                  </td>
                  <td style={{ padding: '8px 10px', fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--color-muted)' }}>
                    {a.track_segment_id}
                  </td>
                  <td style={{ padding: '8px 10px', fontSize: '11px', color: 'var(--color-ink)' }}>
                    {formatMinuteToIST(a.start_minute)} → {formatMinuteToIST(a.end_minute)}
                  </td>
                  <td style={{ padding: '8px 10px', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                    {a.duration_minutes}m
                  </td>
                  <td style={{ padding: '8px 10px', fontSize: '11px' }}>
                    {a.power_block_required ? (
                      <span style={{ color: '#D97706', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '2px' }}>
                        <Zap size={11} /> {a.power_block_section || 'Required'}
                      </span>
                    ) : (
                      <span style={{ color: 'var(--color-muted)' }}>No</span>
                    )}
                  </td>
                  <td style={{ padding: '8px 10px', fontSize: '11px' }}>
                    {a.is_locked ? (
                      <span style={{ color: '#B94D2F', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '2px' }}>
                        <Lock size={11} /> Hard Lock
                      </span>
                    ) : (
                      <span style={{ color: 'var(--color-muted)' }}>Dynamic</span>
                    )}
                  </td>
                  <td style={{ padding: '8px 10px', fontSize: '11px' }}>
                    {a.is_shadow_block ? (
                      <span style={{ color: '#7C3AED', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '2px' }}>
                        <Layers size={11} /> Shadow Bundle
                      </span>
                    ) : (
                      <span>Single Task</span>
                    )}
                  </td>
                  <td style={{ padding: '8px 10px', fontSize: '11px' }}>
                    <span style={{ color: 'var(--color-success)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '2px' }}>
                      <CheckCircle2 size={11} /> Feasible (PASS)
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
