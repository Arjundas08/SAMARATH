import React, { useMemo } from 'react';
import { MaterializedAssignment } from '../../types/api';
import { Wrench, Zap, Users } from 'lucide-react';

interface ResourceTimelineProps {
  assignments: MaterializedAssignment[];
}

const RESOURCES = [
  { id: 'MACH-BCM-01', name: 'BCM-01 (Ballast Cleaning Machine)', type: 'CIVIL', icon: Wrench, color: '#0284C7' },
  { id: 'MACH-CSM-01', name: 'CSM-01 (Continuous Tamping Machine)', type: 'CIVIL', icon: Wrench, color: '#0284C7' },
  { id: 'MACH-TW-01', name: 'Tower Wagon TW-01 (OHE Inspection)', type: 'ELECTRICAL', icon: Zap, color: '#0D9488' },
  { id: 'CREW-ENG-GANG-A', name: 'Permanent Way Gang Alpha', type: 'CREW', icon: Users, color: '#7C3AED' },
  { id: 'CREW-SIG-DIV-01', name: 'S&T Telecom Maintenance Unit', type: 'CREW', icon: Users, color: '#7C3AED' },
];

export const ResourceTimeline: React.FC<ResourceTimelineProps> = ({ assignments }) => {
  // Map assignments to each resource
  const resourceAllocations = useMemo(() => {
    const map: Record<string, MaterializedAssignment[]> = {};
    RESOURCES.forEach((r) => {
      map[r.id] = [];
    });

    assignments.forEach((a) => {
      // Check required resources
      if (a.assigned_resources && a.assigned_resources.length > 0) {
        a.assigned_resources.forEach((req) => {
          if (map[req.resource_id]) {
            map[req.resource_id].push(a);
          }
        });
      } else {
        // Fallback matching by business key / dept
        if (a.business_key.includes('ENG') && map['MACH-BCM-01']) {
          map['MACH-BCM-01'].push(a);
        } else if (a.business_key.includes('ELE') && map['MACH-TW-01']) {
          map['MACH-TW-01'].push(a);
        } else if (a.business_key.includes('SIG') && map['CREW-SIG-DIV-01']) {
          map['CREW-SIG-DIV-01'].push(a);
        }
      }
    });

    return map;
  }, [assignments]);

  const totalMinutes = 10080; // 7 days * 1440m
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

  return (
    <div style={{ backgroundColor: '#FFFFFF', padding: '16px 20px', borderRadius: 'var(--radius-lg)', border: '1px solid var(--color-border)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div>
          <h2 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-ink)' }}>
            Specialized Machinery & Resource Gantt Allocations
          </h2>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
            Coordinated machine possessions and gang assignments across the 7-day operational cycle.
          </div>
        </div>
        <div style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--color-muted)' }}>
          Horizon: 7 Days (10,080 min)
        </div>
      </div>

      {/* Days Scale Header */}
      <div style={{ display: 'flex', marginLeft: '240px', borderBottom: '1px solid var(--color-border)', paddingBottom: '4px', marginBottom: '8px' }}>
        {days.map((day, idx) => (
          <div
            key={idx}
            style={{
              flex: 1,
              textAlign: 'center',
              fontSize: '10px',
              fontWeight: 600,
              color: 'var(--color-muted)',
              borderRight: idx < 6 ? '1px dashed var(--color-border)' : 'none',
            }}
          >
            {day} 1{2 + idx} Oct
          </div>
        ))}
      </div>

      {/* Resource Rows */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {RESOURCES.map((r) => {
          const allocated = resourceAllocations[r.id] || [];
          const Icon = r.icon;

          return (
            <div
              key={r.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                backgroundColor: 'var(--color-surface-warm)',
                padding: '8px 10px',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)',
              }}
            >
              {/* Resource Label Column */}
              <div style={{ width: '230px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div
                  style={{
                    width: '24px',
                    height: '24px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: `${r.color}15`,
                    color: r.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Icon size={13} />
                </div>
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-ink)' }}>
                    {r.name}
                  </div>
                  <div style={{ fontSize: '9px', fontFamily: 'var(--font-mono)', color: 'var(--color-muted)' }}>
                    {allocated.length} possessions assigned
                  </div>
                </div>
              </div>

              {/* Gantt Bar Lane */}
              <div
                style={{
                  flex: 1,
                  height: '24px',
                  backgroundColor: '#FFFFFF',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--color-border)',
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                {/* Day divider lines */}
                {[1, 2, 3, 4, 5, 6].map((dayIdx) => (
                  <div
                    key={dayIdx}
                    style={{
                      position: 'absolute',
                      left: `${(dayIdx / 7) * 100}%`,
                      top: 0,
                      bottom: 0,
                      width: '1px',
                      backgroundColor: '#E8EEF2',
                      zIndex: 1,
                    }}
                  />
                ))}

                {/* Allocated Intervals */}
                {allocated.map((a, aIdx) => {
                  const leftPct = Math.max(0, (a.start_minute / totalMinutes) * 100);
                  const widthPct = Math.max(0.6, (a.duration_minutes / totalMinutes) * 100);

                  return (
                    <div
                      key={aIdx}
                      title={`${a.business_key} (${a.duration_minutes}m on ${a.track_segment_id})`}
                      style={{
                        position: 'absolute',
                        left: `${leftPct}%`,
                        width: `${widthPct}%`,
                        top: '2px',
                        bottom: '2px',
                        backgroundColor: r.color,
                        borderRadius: '2px',
                        zIndex: 2,
                        boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#FFFFFF',
                        fontSize: '9px',
                        fontWeight: 600,
                        overflow: 'hidden',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      {widthPct > 3 ? a.business_key.split('-').slice(-1)[0] : ''}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
