import React, { useState, useEffect } from 'react';
import { Search, Zap, RefreshCw, AlertCircle, Database, CheckCircle2, SlidersHorizontal } from 'lucide-react';
import { Task } from '../types/api';
import { StatusBadge } from '../components/common/StatusBadge';
import { EvidenceDrawer } from '../components/common/EvidenceDrawer';
import { EmptyState } from '../components/common/EmptyState';
import { ProvenanceBadge } from '../components/common/ProvenanceBadge';

interface MaintenanceViewProps {
  onSelectTask?: (task: Task) => void;
}

export const MaintenanceView: React.FC<MaintenanceViewProps> = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDepartment, setSelectedDepartment] = useState<string>('ALL');
  const [selectedCriticality, setSelectedCriticality] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isSeeding, setIsSeeding] = useState<boolean>(false);
  const [seedNotification, setSeedNotification] = useState<string | null>(null);

  const fetchTasks = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/v1/tasks?limit=200');
      if (!res.ok) {
        throw new Error(`Failed to fetch tasks: HTTP ${res.status}`);
      }
      const data = await res.json();
      setTasks(data.tasks || []);
    } catch (err: any) {
      setError(err.message || 'Error fetching tasks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleSeedCorridor = async () => {
    setIsSeeding(true);
    setSeedNotification(null);
    try {
      const res = await fetch('/api/v1/gateway/seed/corridor', { method: 'POST' });
      if (!res.ok) {
        throw new Error(`Seed failed: HTTP ${res.status}`);
      }
      const data = await res.json();
      setSeedNotification(
        `Successfully seeded ${data.corridor_code} corridor: 6 stations, 10 track segments, ${data.tasks_seeded} monthly tasks, ${data.resource_calendars_count} resource calendars.`
      );
      await fetchTasks();
    } catch (err: any) {
      setError(err.message || 'Error seeding corridor');
    } finally {
      setIsSeeding(false);
    }
  };

  // Filter tasks based on search, department, and criticality
  const filteredTasks = tasks.filter((task) => {
    const matchesDept = selectedDepartment === 'ALL' || task.department === selectedDepartment;
    const matchesCrit = selectedCriticality === 'ALL' || task.criticality === selectedCriticality;
    const matchesSearch =
      searchQuery === '' ||
      task.business_key.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.track_segment_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.station_from.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.station_to.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesDept && matchesCrit && matchesSearch;
  });

  // Calculate live database counts
  const totalCount = tasks.length;
  const engCount = tasks.filter((t) => t.department === 'ENGINEERING').length;
  const electCount = tasks.filter((t) => t.department === 'ELECTRICAL').length;
  const sigCount = tasks.filter((t) => t.department === 'SIGNALLING').length;
  const tier1Count = tasks.filter((t) => t.criticality === 'TIER_1_MANDATORY').length;
  const powerBlockCount = tasks.filter((t) => t.requires_power_block).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Banner */}
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '18px', fontWeight: 700, color: 'var(--color-ink)' }}>
              Maintenance Demands (Integrated Repositories)
            </h1>
            <ProvenanceBadge mode="TEST" />
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-muted)', marginTop: '2px' }}>
            Consolidated engineering requirements from TMS (P-Way), TDMS (TRD), and SMMS (S&T)
          </div>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <button
            onClick={fetchTasks}
            disabled={loading}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 12px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-border)',
              backgroundColor: 'var(--color-surface)',
              color: 'var(--color-ink)',
              fontSize: '12px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>

          <button
            onClick={handleSeedCorridor}
            disabled={isSeeding}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: 'var(--radius-md)',
              border: 'none',
              backgroundColor: 'var(--color-action)',
              color: '#ffffff',
              fontSize: '12px',
              fontWeight: 600,
              cursor: isSeeding ? 'not-allowed' : 'pointer',
            }}
          >
            <Database size={14} />
            <span>{isSeeding ? 'Seeding...' : 'Seed VKC Corridor (60 Tasks)'}</span>
          </button>
        </div>
      </div>

      {seedNotification && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            backgroundColor: 'rgba(0, 109, 119, 0.1)',
            border: '1px solid var(--color-action)',
            borderRadius: 'var(--radius-md)',
            padding: '12px 16px',
            color: 'var(--color-action)',
            fontSize: '13px',
          }}
        >
          <CheckCircle2 size={16} />
          <span>{seedNotification}</span>
        </div>
      )}

      {error && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            backgroundColor: 'rgba(179, 54, 54, 0.1)',
            border: '1px solid var(--color-critical)',
            borderRadius: 'var(--radius-md)',
            padding: '12px 16px',
            color: 'var(--color-critical)',
            fontSize: '13px',
          }}
        >
          <AlertCircle size={16} />
          <span>{error}</span>
        </div>
      )}

      {/* Dynamic Metric Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
        <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Total Demands</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-ink)', marginTop: '4px' }}>{totalCount}</div>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>Live in SQLite DB</div>
        </div>

        <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Engineering (P-Way)</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#1B4965', marginTop: '4px' }}>{engCount}</div>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>Track & Turnout</div>
        </div>

        <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Electrical (TRD)</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-action)', marginTop: '4px' }}>{electCount}</div>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>OHE & Cantilever</div>
        </div>

        <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Signalling (S&T)</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: '#4A5568', marginTop: '4px' }}>{sigCount}</div>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>Point & Interlocking</div>
        </div>

        <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600, textTransform: 'uppercase' }}>Mandatory / Power Block</div>
          <div style={{ fontSize: '24px', fontWeight: 700, color: 'var(--color-warning)', marginTop: '4px' }}>
            {tier1Count} <span style={{ fontSize: '14px', fontWeight: 400, color: 'var(--color-muted)' }}>/ {powerBlockCount} OHE</span>
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>Tier 1 / Isolation req.</div>
        </div>
      </div>

      {/* Filters and Controls */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '16px',
          flexWrap: 'wrap',
          backgroundColor: 'var(--color-surface)',
          padding: '12px 16px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--color-border)',
        }}
      >
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-muted)', marginRight: '4px' }}>Dept:</span>
          {['ALL', 'ENGINEERING', 'ELECTRICAL', 'SIGNALLING'].map((dept) => (
            <button
              key={dept}
              onClick={() => setSelectedDepartment(dept)}
              style={{
                padding: '6px 12px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid',
                borderColor: selectedDepartment === dept ? 'var(--color-action)' : 'var(--color-border)',
                backgroundColor: selectedDepartment === dept ? 'rgba(0, 109, 119, 0.1)' : 'transparent',
                color: selectedDepartment === dept ? 'var(--color-action)' : 'var(--color-ink)',
                fontSize: '11px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              {dept}
            </button>
          ))}
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <SlidersHorizontal size={14} color="var(--color-muted)" />
            <select
              value={selectedCriticality}
              onChange={(e) => setSelectedCriticality(e.target.value)}
              style={{
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-surface)',
                color: 'var(--color-ink)',
                fontSize: '12px',
              }}
            >
              <option value="ALL">All Criticality Tiers</option>
              <option value="TIER_1_MANDATORY">Tier 1 - Mandatory Safety</option>
              <option value="TIER_2_SPEED_RESTRICTION">Tier 2 - Speed Restriction</option>
              <option value="TIER_3_CYCLIC">Tier 3 - Cyclic Maintenance</option>
            </select>
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              border: '1px solid var(--color-border)',
              borderRadius: 'var(--radius-sm)',
              padding: '6px 10px',
              backgroundColor: '#ffffff',
            }}
          >
            <Search size={14} color="var(--color-muted)" />
            <input
              type="text"
              placeholder="Search by key, description, track..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                border: 'none',
                outline: 'none',
                fontSize: '12px',
                width: '220px',
                backgroundColor: 'transparent',
              }}
            />
          </div>
        </div>
      </div>

      {/* Task List Table */}
      {loading ? (
        <div style={{ padding: '60px', textAlign: 'center', color: 'var(--color-muted)' }}>
          <RefreshCw size={24} className="animate-spin" style={{ margin: '0 auto 12px auto' }} />
          <div>Loading maintenance demands from SQLite repository...</div>
        </div>
      ) : filteredTasks.length === 0 ? (
        <EmptyState
          icon={Database}
          title={tasks.length === 0 ? 'No Demands Loaded in Database' : 'No Demands Match Active Filters'}
          description={
            tasks.length === 0
              ? 'Click "Seed VKC Corridor" to load 60 monthly tasks, 6 stations, 10 track segments, and 11 qualified resource gangs.'
              : 'Try clearing your search query or switching department / criticality filters.'
          }
          actionLabel={tasks.length === 0 ? 'Seed Corridor Now' : 'Clear Filters'}
          onAction={tasks.length === 0 ? handleSeedCorridor : () => { setSelectedDepartment('ALL'); setSelectedCriticality('ALL'); setSearchQuery(''); }}
        />
      ) : (
        <div
          style={{
            backgroundColor: 'var(--color-surface)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-border)',
            overflowX: 'auto',
          }}
        >
          <table style={{ width: '100%', minWidth: '900px', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead>
              <tr style={{ backgroundColor: 'var(--color-canvas)', borderBottom: '1px solid var(--color-border)', textAlign: 'left' }}>
                <th style={{ padding: '10px 14px', fontWeight: 600, whiteSpace: 'nowrap' }}>Business Key</th>
                <th style={{ padding: '10px 14px', fontWeight: 600, whiteSpace: 'nowrap' }}>Department</th>
                <th style={{ padding: '10px 14px', fontWeight: 600 }}>Work Scope</th>
                <th style={{ padding: '10px 14px', fontWeight: 600, whiteSpace: 'nowrap' }}>Location (Km)</th>
                <th style={{ padding: '10px 14px', fontWeight: 600, whiteSpace: 'nowrap' }}>Duration</th>
                <th style={{ padding: '10px 14px', fontWeight: 600, whiteSpace: 'nowrap' }}>Criticality</th>
                <th style={{ padding: '10px 14px', fontWeight: 600, whiteSpace: 'nowrap' }}>Power Block</th>
                <th style={{ padding: '10px 14px', fontWeight: 600, whiteSpace: 'nowrap' }}>Deadline (UTC)</th>
                <th style={{ padding: '10px 14px', fontWeight: 600, whiteSpace: 'nowrap' }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredTasks.map((t) => (
                <tr
                  key={t.task_id}
                  onClick={() => setSelectedTask(t)}
                  style={{
                    borderBottom: '1px solid var(--color-border)',
                    cursor: 'pointer',
                    backgroundColor: selectedTask?.task_id === t.task_id ? 'rgba(0, 109, 119, 0.05)' : 'transparent',
                    transition: 'background-color 0.15s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(0, 0, 0, 0.02)')}
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.backgroundColor = selectedTask?.task_id === t.task_id ? 'rgba(0, 109, 119, 0.05)' : 'transparent')
                  }
                >
                  <td style={{ padding: '12px 14px', fontWeight: 700, fontFamily: 'monospace', color: 'var(--color-action)', whiteSpace: 'nowrap' }}>
                    {t.business_key}
                  </td>
                  <td style={{ padding: '12px 14px', whiteSpace: 'nowrap' }}>
                    <span
                      style={{
                        padding: '2px 6px',
                        borderRadius: '4px',
                        fontSize: '10px',
                        fontWeight: 700,
                        backgroundColor:
                          t.department === 'ENGINEERING'
                            ? 'rgba(27, 73, 101, 0.1)'
                            : t.department === 'ELECTRICAL'
                            ? 'rgba(0, 109, 119, 0.1)'
                            : 'rgba(74, 85, 104, 0.1)',
                        color:
                          t.department === 'ENGINEERING'
                            ? '#1B4965'
                            : t.department === 'ELECTRICAL'
                            ? 'var(--color-action)'
                            : '#4A5568',
                      }}
                    >
                      {t.department}
                    </span>
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <div style={{ fontWeight: 600, color: 'var(--color-ink)' }}>{t.work_type}</div>
                    <div style={{ fontSize: '11px', color: 'var(--color-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '240px' }}>
                      {t.description}
                    </div>
                  </td>
                  <td style={{ padding: '12px 14px', whiteSpace: 'nowrap' }}>
                    <div style={{ fontWeight: 600 }}>{t.track_segment_id}</div>
                    <div style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
                      {t.station_from} → {t.station_to} (Km {t.chainage_start_km.toFixed(1)} - {t.chainage_end_km.toFixed(1)})
                    </div>
                  </td>
                  <td style={{ padding: '12px 14px', whiteSpace: 'nowrap' }}>
                    <div style={{ fontWeight: 600 }}>{t.duration_minutes} min</div>
                    <div style={{ fontSize: '11px', color: 'var(--color-muted)' }}>Total: {t.total_block_minutes} min</div>
                  </td>
                  <td style={{ padding: '12px 14px', whiteSpace: 'nowrap' }}>
                    <StatusBadge status={t.criticality} />
                  </td>
                  <td style={{ padding: '12px 14px', whiteSpace: 'nowrap' }}>
                    {t.requires_power_block ? (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-action)', fontWeight: 600, fontSize: '11px' }}>
                        <Zap size={14} />
                        <span>{t.power_block_elementary_section || 'Required'}</span>
                      </div>
                    ) : (
                      <span style={{ color: 'var(--color-muted)', fontSize: '11px' }}>None</span>
                    )}
                  </td>
                  <td style={{ padding: '12px 14px', fontSize: '11px', color: 'var(--color-muted)', whiteSpace: 'nowrap' }}>
                    {t.deadline_utc ? t.deadline_utc.split('T')[0] : 'N/A'}
                  </td>
                  <td style={{ padding: '12px 14px' }}>
                    <StatusBadge status={t.demand_status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Task Evidence Drawer */}
      <EvidenceDrawer
        task={selectedTask}
        isOpen={Boolean(selectedTask)}
        onClose={() => setSelectedTask(null)}
      />
    </div>
  );
};
