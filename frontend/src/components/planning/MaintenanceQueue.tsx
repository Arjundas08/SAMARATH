import React, { useState, useMemo } from 'react';
import { Task, MaterializedAssignment } from '../../types/api';
import { Search, Lock, CheckCircle2, Clock } from 'lucide-react';

interface MaintenanceQueueProps {
  tasks: Task[];
  assignments: MaterializedAssignment[];
  selectedTask: Task | null;
  onSelectTask: (task: Task) => void;
  onSelectAssignment: (assignment: MaterializedAssignment | null) => void;
}

export const MaintenanceQueue: React.FC<MaintenanceQueueProps> = ({
  tasks,
  assignments,
  selectedTask,
  onSelectTask,
  onSelectAssignment,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'SCHEDULED' | 'UNSCHEDULED' | 'LOCKED'>('ALL');
  const [deptFilter, setDeptFilter] = useState<string>('ALL');

  // Map task_id to assignment for quick lookup
  const assignmentByTaskId = useMemo(() => {
    const map = new Map<string, MaterializedAssignment>();
    assignments.forEach((a) => {
      map.set(a.task_id, a);
      if (a.bundled_with_task_ids) {
        a.bundled_with_task_ids.forEach((tid) => map.set(tid, a));
      }
    });
    return map;
  }, [assignments]);

  // Filter tasks
  const filteredTasks = useMemo(() => {
    return tasks.filter((t) => {
      const assignment = assignmentByTaskId.get(t.task_id);
      const isScheduled = !!assignment;
      const isLocked = assignment?.is_locked;

      if (statusFilter === 'SCHEDULED' && !isScheduled) return false;
      if (statusFilter === 'UNSCHEDULED' && isScheduled) return false;
      if (statusFilter === 'LOCKED' && !isLocked) return false;

      if (deptFilter !== 'ALL' && t.department !== deptFilter) return false;

      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        return (
          t.business_key.toLowerCase().includes(q) ||
          t.description.toLowerCase().includes(q) ||
          t.track_segment_id.toLowerCase().includes(q) ||
          t.work_type.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [tasks, assignmentByTaskId, statusFilter, deptFilter, searchQuery]);

  const handleTaskClick = (t: Task) => {
    onSelectTask(t);
    const assign = assignmentByTaskId.get(t.task_id) || null;
    onSelectAssignment(assign);
  };

  const getDeptColor = (dept: string) => {
    switch (dept) {
      case 'ENGINEERING':
        return '#0284C7';
      case 'ELECTRICAL':
        return '#0D9488';
      case 'SIGNALLING':
        return '#7C3AED';
      default:
        return '#526478';
    }
  };

  return (
    <div
      style={{
        width: '100%',
        minWidth: '240px',
        backgroundColor: 'var(--color-surface)',
        borderRight: '1px solid var(--color-border)',
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '12px 14px',
          borderBottom: '1px solid var(--color-border)',
          backgroundColor: 'var(--color-surface-warm)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--color-ink)' }}>
            Maintenance Queue
          </div>
          <span
            style={{
              fontSize: '11px',
              fontFamily: 'var(--font-mono)',
              fontWeight: 700,
              color: 'var(--color-action)',
              backgroundColor: 'var(--color-action-tint)',
              padding: '1px 6px',
              borderRadius: 'var(--radius-sm)',
            }}
          >
            {assignments.length}/{tasks.length} Placed
          </span>
        </div>

        {/* Search */}
        <div style={{ position: 'relative', marginBottom: '8px' }}>
          <Search
            size={12}
            color="var(--color-muted)"
            style={{ position: 'absolute', left: '8px', top: '7px' }}
          />
          <input
            type="text"
            placeholder="Search key, work, segment..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '5px 8px 5px 26px',
              fontSize: '11px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-border)',
              backgroundColor: '#FFFFFF',
              color: 'var(--color-ink)',
            }}
          />
        </div>

        {/* Status Filter Buttons */}
        <div style={{ display: 'flex', gap: '3px', marginBottom: '4px' }}>
          {(['ALL', 'SCHEDULED', 'UNSCHEDULED', 'LOCKED'] as const).map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              style={{
                flex: 1,
                padding: '3px 0',
                fontSize: '9px',
                fontWeight: statusFilter === st ? 700 : 500,
                border: 'none',
                borderRadius: '3px',
                backgroundColor: statusFilter === st ? 'var(--color-ink)' : 'transparent',
                color: statusFilter === st ? '#FFFFFF' : 'var(--color-muted)',
                cursor: 'pointer',
                textAlign: 'center',
              }}
            >
              {st === 'ALL' ? 'All' : st === 'SCHEDULED' ? 'Placed' : st === 'UNSCHEDULED' ? 'Unplaced' : 'Locked'}
            </button>
          ))}
        </div>

        {/* Department Filter */}
        <select
          value={deptFilter}
          onChange={(e) => setDeptFilter(e.target.value)}
          style={{
            width: '100%',
            padding: '3px 6px',
            fontSize: '10px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--color-border)',
            backgroundColor: '#FFFFFF',
            color: 'var(--color-ink)',
            marginTop: '4px',
          }}
        >
          <option value="ALL">All Departments</option>
          <option value="ENGINEERING">Civil / Track (ENG)</option>
          <option value="ELECTRICAL">Electrical / OHE (ELE)</option>
          <option value="SIGNALLING">Signalling (SIG)</option>
        </select>
      </div>

      {/* Task List */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '6px' }}>
        {filteredTasks.length === 0 ? (
          <div style={{ padding: '24px 12px', textAlign: 'center', color: 'var(--color-muted)', fontSize: '11px' }}>
            No tasks match your filter criteria.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {filteredTasks.map((t) => {
              const assign = assignmentByTaskId.get(t.task_id);
              const isSelected = selectedTask?.task_id === t.task_id;
              const isScheduled = !!assign;
              const deptColor = getDeptColor(t.department);

              return (
                <div
                  key={t.task_id}
                  onClick={() => handleTaskClick(t)}
                  style={{
                    padding: '8px 10px',
                    borderRadius: 'var(--radius-md)',
                    border: `1px solid ${isSelected ? 'var(--color-action)' : 'var(--color-border)'}`,
                    backgroundColor: isSelected ? 'var(--color-action-tint)' : '#FFFFFF',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    boxShadow: isSelected ? 'var(--shadow-sm)' : 'none',
                  }}
                >
                  {/* Top Row: Business Key, Department Pill, Status */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <span
                        style={{
                          width: '6px',
                          height: '6px',
                          borderRadius: '50%',
                          backgroundColor: deptColor,
                        }}
                      />
                      <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-ink)' }}>
                        {t.business_key}
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      {assign?.is_locked && <Lock size={10} color="#B94D2F" />}
                      {isScheduled ? (
                        <span
                          style={{
                            fontSize: '9px',
                            fontWeight: 700,
                            color: 'var(--color-success)',
                            backgroundColor: 'var(--color-success-pale)',
                            padding: '1px 5px',
                            borderRadius: '3px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '2px',
                          }}
                        >
                          <CheckCircle2 size={8} /> Placed
                        </span>
                      ) : (
                        <span
                          style={{
                            fontSize: '9px',
                            fontWeight: 600,
                            color: 'var(--color-warning)',
                            backgroundColor: 'var(--color-warning-pale)',
                            padding: '1px 5px',
                            borderRadius: '3px',
                          }}
                        >
                          Unplaced
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Description / Work type */}
                  <div
                    style={{
                      fontSize: '11px',
                      color: 'var(--color-muted)',
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      marginBottom: '4px',
                    }}
                  >
                    {t.work_type}: {t.description}
                  </div>

                  {/* Footer Row: Segment, Duration, Power Block */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '10px', color: 'var(--color-muted)' }}>
                    <span style={{ fontFamily: 'var(--font-mono)' }}>{t.track_segment_id}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '2px' }}>
                      <Clock size={9} /> {t.duration_minutes}m
                    </span>
                    {t.requires_power_block && (
                      <span style={{ color: '#D97706', fontWeight: 700 }}>⚡ OHE</span>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
