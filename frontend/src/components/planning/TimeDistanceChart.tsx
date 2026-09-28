import React, { useEffect, useRef, useState, useMemo } from 'react';
import * as echarts from 'echarts';
import { MaterializedAssignment, StationInfo, TrackSegmentInfo } from '../../types/api';
import { ZoomIn, ZoomOut, RotateCcw, Filter, Eye, EyeOff } from 'lucide-react';

interface TrainOccupationData {
  occupation_id: string;
  train_number: string;
  train_type: string;
  track_segment_id: string;
  entry_time_utc: string;
  exit_time_utc: string;
  start_minute: number;
  end_minute: number;
}

interface TimeDistanceChartProps {
  assignments: MaterializedAssignment[];
  selectedAssignment: MaterializedAssignment | null;
  onSelectAssignment: (assignment: MaterializedAssignment | null) => void;
  stations?: StationInfo[];
  trackSegments?: TrackSegmentInfo[];
  occupations?: TrainOccupationData[];
  horizonStart?: string;
}

// Station chainage mapping for Corridor VKC (Alpha to Foxtrot)
const DEFAULT_STATIONS: StationInfo[] = [
  { station_code: 'ALP', station_name: 'Alpha', chainage_km: 0.0, absolute_distance_meters: 0, total_lines: 4, has_crossover: true },
  { station_code: 'BRV', station_name: 'Bravo', chainage_km: 22.5, absolute_distance_meters: 22500, total_lines: 3, has_crossover: true },
  { station_code: 'CHR', station_name: 'Charlie', chainage_km: 48.0, absolute_distance_meters: 48000, total_lines: 4, has_crossover: true },
  { station_code: 'DLT', station_name: 'Delta', chainage_km: 73.2, absolute_distance_meters: 73200, total_lines: 3, has_crossover: true },
  { station_code: 'ECH', station_name: 'Echo', chainage_km: 96.8, absolute_distance_meters: 96800, total_lines: 2, has_crossover: false },
  { station_code: 'FXT', station_name: 'Foxtrot', chainage_km: 120.0, absolute_distance_meters: 120000, total_lines: 4, has_crossover: true },
];

// Department colors (Signal & Slate theme)
const DEPT_COLORS: Record<string, string> = {
  ENG: '#0284C7', // Civil / Track - Steel Blue
  CIVIL: '#0284C7',
  ENGINEERING: '#0284C7',
  ELE: '#0D9488', // Electrical / Traction - Teal
  ELECTRICAL: '#0D9488',
  SIG: '#7C3AED', // S&T / Signalling - Purple
  SIGNALLING: '#7C3AED',
  BUNDLE: '#142B3E', // Multi-department Shadow block - Dark Slate
};

const TRAIN_COLORS: Record<string, string> = {
  PASSENGER: '#3B82F6', // Blue
  EXPRESS: '#DC2626',   // Crimson
  RAJDHANI: '#DC2626',
  FREIGHT: '#D97706',   // Burnt Orange / Amber
};

export const TimeDistanceChart: React.FC<TimeDistanceChartProps> = ({
  assignments,
  selectedAssignment,
  onSelectAssignment,
  stations = DEFAULT_STATIONS,
  occupations = [],
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);

  // Filter States
  const [directionFilter, setDirectionFilter] = useState<'ALL' | 'UP' | 'DOWN'>('ALL');
  const [departmentFilter, setDepartmentFilter] = useState<string>('ALL');
  const [showTrains, setShowTrains] = useState<boolean>(true);
  const [selectedDay, setSelectedDay] = useState<number>(0); // 0 = Full Week (Days 1-7), 1-7 = Specific Day

  // Segment to KM bounds lookup
  const segmentBounds = useMemo(() => {
    return {
      'SEC-01-UP': { startKm: 0.0, endKm: 22.5, dir: 'UP' },
      'SEC-01-DN': { startKm: 0.0, endKm: 22.5, dir: 'DOWN' },
      'SEC-02-UP': { startKm: 22.5, endKm: 48.0, dir: 'UP' },
      'SEC-02-DN': { startKm: 22.5, endKm: 48.0, dir: 'DOWN' },
      'SEC-03-UP': { startKm: 48.0, endKm: 73.2, dir: 'UP' },
      'SEC-03-DN': { startKm: 48.0, endKm: 73.2, dir: 'DOWN' },
      'SEC-04-UP': { startKm: 73.2, endKm: 96.8, dir: 'UP' },
      'SEC-04-DN': { startKm: 73.2, endKm: 96.8, dir: 'DOWN' },
      'SEC-05-UP': { startKm: 96.8, endKm: 120.0, dir: 'UP' },
      'SEC-05-DN': { startKm: 96.8, endKm: 120.0, dir: 'DOWN' },
    };
  }, []);

  // Filter assignments
  const filteredAssignments = useMemo(() => {
    return assignments.filter((a) => {
      const seg = segmentBounds[a.track_segment_id as keyof typeof segmentBounds];
      if (directionFilter !== 'ALL' && seg && seg.dir !== directionFilter) {
        return false;
      }
      if (departmentFilter !== 'ALL') {
        const dept = a.business_key.split('-')[1] || '';
        if (departmentFilter === 'ENG' && !dept.includes('ENG') && !dept.includes('CIVIL')) return false;
        if (departmentFilter === 'ELE' && !dept.includes('ELE') && !dept.includes('OHE')) return false;
        if (departmentFilter === 'SIG' && !dept.includes('SIG')) return false;
      }
      return true;
    });
  }, [assignments, directionFilter, departmentFilter, segmentBounds]);

  // Filter train occupations
  const filteredOccupations = useMemo(() => {
    if (!showTrains) return [];
    return occupations.filter((occ) => {
      const seg = segmentBounds[occ.track_segment_id as keyof typeof segmentBounds];
      if (directionFilter !== 'ALL' && seg && seg.dir !== directionFilter) {
        return false;
      }
      return true;
    });
  }, [occupations, showTrains, directionFilter, segmentBounds]);

  // Determine time window based on selected day (0 = whole week, 1..7 = 1440 min slices)
  const [minMinute, maxMinute] = useMemo(() => {
    if (selectedDay === 0) {
      return [0, 10080]; // 7 days * 24h * 60m
    }
    const start = (selectedDay - 1) * 1440;
    const end = selectedDay * 1440;
    return [start, end];
  }, [selectedDay]);

  // Format minute of week to Asia/Kolkata date & time
  const formatMinuteToIST = (minute: number): string => {
    // Horizon starts Mon 12 Oct 2026 00:00 UTC = 05:30 IST
    const days = ['Mon 12', 'Tue 13', 'Wed 14', 'Thu 15', 'Fri 16', 'Sat 17', 'Sun 18'];
    const dayIdx = Math.min(6, Math.floor(minute / 1440));
    const dayMinute = minute % 1440;
    const hours = Math.floor(dayMinute / 60);
    const mins = dayMinute % 60;
    return `${days[dayIdx]} ${String(hours).padStart(2, '0')}:${String(mins).padStart(2, '0')}`;
  };

  const onSelectRef = useRef(onSelectAssignment);
  onSelectRef.current = onSelectAssignment;

  useEffect(() => {
    return () => {
      if (chartInstance.current) {
        chartInstance.current.dispose();
        chartInstance.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!chartRef.current) return;

    if (!chartInstance.current) {
      chartInstance.current = echarts.getInstanceByDom(chartRef.current) || echarts.init(chartRef.current);

      chartInstance.current.on('click', (params: any) => {
        if (params.componentType === 'series' && params.data && params.data.assignment) {
          onSelectRef.current(params.data.assignment);
        }
      });
    }

    const chart = chartInstance.current;

    // Build Custom Maintenance Blocks Data
    // ECharts custom series renders rectangles: [startMinute, startKm, endMinute, endKm]
    const maintenanceData = filteredAssignments.map((a) => {
      const bounds = segmentBounds[a.track_segment_id as keyof typeof segmentBounds] || { startKm: 0, endKm: 22.5 };
      const deptCode = a.business_key.includes('ENG')
        ? 'ENG'
        : a.business_key.includes('ELE')
        ? 'ELE'
        : a.business_key.includes('SIG')
        ? 'SIG'
        : 'BUNDLE';
      const color = DEPT_COLORS[deptCode] || '#006D77';
      const isSelected = selectedAssignment?.assignment_id === a.assignment_id;

      return {
        name: a.business_key,
        value: [a.start_minute, bounds.startKm, a.end_minute, bounds.endKm, a.duration_minutes],
        itemStyle: {
          color: color,
          borderColor: isSelected ? '#FFD700' : a.is_locked ? '#B94D2F' : color,
          borderWidth: isSelected ? 3 : a.is_locked ? 2 : 1,
          borderType: a.is_locked ? 'solid' : 'solid',
          opacity: isSelected ? 0.95 : 0.85,
        },
        assignment: a,
      };
    });

    // Build Train Occupation Trajectories Data
    // Group occupations by train_number to draw connected string paths
    const trainPaths: Record<string, TrainOccupationData[]> = {};
    filteredOccupations.forEach((occ) => {
      if (!trainPaths[occ.train_number]) {
        trainPaths[occ.train_number] = [];
      }
      trainPaths[occ.train_number].push(occ);
    });

    const trainLineSeries: any[] = [];
    Object.entries(trainPaths).forEach(([trainNum, occs]) => {
      occs.sort((a, b) => a.start_minute - b.start_minute);
      const trainType = occs[0]?.train_type || 'PASSENGER';
      const color = TRAIN_COLORS[trainType] || '#3B82F6';
      const isFreight = trainType === 'FREIGHT';

      // Build points: each occupation has [start_minute, startKm] and [end_minute, endKm]
      const points: [number, number][] = [];
      occs.forEach((occ) => {
        const bounds = segmentBounds[occ.track_segment_id as keyof typeof segmentBounds];
        if (!bounds) return;
        const isUp = bounds.dir === 'UP';
        // UP trains travel from FXT (120km) to ALP (0km)
        // DOWN trains travel from ALP (0km) to FXT (120km)
        const entryKm = isUp ? bounds.endKm : bounds.startKm;
        const exitKm = isUp ? bounds.startKm : bounds.endKm;
        points.push([occ.start_minute, entryKm]);
        points.push([occ.end_minute, exitKm]);
      });

      if (points.length >= 2) {
        trainLineSeries.push({
          type: 'line',
          name: `Train ${trainNum} (${trainType})`,
          data: points,
          smooth: false,
          showSymbol: false,
          lineStyle: {
            color: color,
            width: isFreight ? 1.5 : 2,
            type: isFreight ? 'dashed' : 'solid',
            opacity: 0.65,
          },
          emphasis: {
            lineStyle: {
              width: 3.5,
              opacity: 1,
            },
          },
          z: 2,
        });
      }
    });

    // Custom Series Render Function for Maintenance Blocks
    const renderMaintenanceBlock = (_params: any, api: any) => {
      const start = api.coord([api.value(0), api.value(1)]);
      const end = api.coord([api.value(2), api.value(3)]);
      const width = Math.max(end[0] - start[0], 6);
      const height = Math.abs(end[1] - start[1]);
      const y = Math.min(start[1], end[1]);

      const style = api.style();

      return {
        type: 'group',
        children: [
          {
            type: 'rect',
            shape: {
              x: start[0],
              y: y,
              width: width,
              height: height,
              r: [4, 4, 4, 4],
            },
            style: style,
          },
          // Phase Breakdown indicator (subtle inner stripe if width allows)
          width > 40
            ? {
                type: 'text',
                style: {
                  text: api.value(4) + 'm',
                  x: start[0] + width / 2,
                  y: y + height / 2,
                  textAlign: 'center',
                  textVerticalAlign: 'middle',
                  fill: '#FFFFFF',
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 10,
                  fontWeight: 600,
                },
              }
            : null,
        ].filter(Boolean),
      };
    };

    const option: echarts.EChartsOption = {
      backgroundColor: '#FFFFFF',
      title: {
        text: 'Corridor VKC Time-Distance String Chart',
        subtext: 'Horizontal: Time (Asia/Kolkata) | Vertical: Spatial Chainage (Km 0.0 - 120.0)',
        left: 20,
        top: 12,
        textStyle: {
          color: '#142B3E',
          fontSize: 14,
          fontWeight: 700,
          fontFamily: 'Inter, sans-serif',
        },
        subtextStyle: {
          color: '#526478',
          fontSize: 11,
          fontFamily: 'Inter, sans-serif',
        },
      },
      legend: {
        right: 20,
        top: 16,
        data: ['Civil (ENG)', 'Electrical (ELE)', 'S&T (SIG)', 'Passenger Train', 'Freight Train'],
        textStyle: {
          color: '#526478',
          fontSize: 11,
        },
        icon: 'roundRect',
      },
      tooltip: {
        trigger: 'item',
        backgroundColor: '#142B3E',
        borderColor: '#006D77',
        borderWidth: 1,
        textStyle: {
          color: '#FFFFFF',
          fontSize: 12,
        },
        formatter: (params: any) => {
          if (params.data && params.data.assignment) {
            const a: MaterializedAssignment = params.data.assignment;
            const startStr = formatMinuteToIST(a.start_minute);
            const endStr = formatMinuteToIST(a.end_minute);
            return `
              <div style="padding: 4px; min-width: 220px;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 4px; margin-bottom: 6px;">
                  <span style="font-weight: 700; color: #5EEAD4;">${a.business_key}</span>
                  <span style="font-size: 10px; background: rgba(255,255,255,0.15); padding: 2px 6px; border-radius: 3px;">${a.track_segment_id}</span>
                </div>
                <div style="font-size: 11px; margin-bottom: 3px;"><b>Window:</b> ${startStr} → ${endStr} (${a.duration_minutes}m)</div>
                <div style="font-size: 11px; margin-bottom: 3px;"><b>Power Block:</b> ${a.power_block_required ? '⚡ Required (' + (a.power_block_section || 'Yes') + ')' : 'None'}</div>
                <div style="font-size: 11px; margin-bottom: 3px;"><b>Hard Lock:</b> ${a.is_locked ? '🔒 Yes' : 'No'}</div>
                <div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">Click to view Evidence & Readiness</div>
              </div>
            `;
          } else if (params.seriesType === 'line') {
            return `
              <div style="padding: 4px;">
                <div style="font-weight: 700; color: #93C5FD;">${params.seriesName}</div>
                <div style="font-size: 11px; margin-top: 4px;">Time: ${formatMinuteToIST(params.value[0])}</div>
                <div style="font-size: 11px;">Chainage: Km ${params.value[1].toFixed(1)}</div>
              </div>
            `;
          }
          return '';
        },
      },
      grid: {
        left: 90,
        right: 40,
        top: 65,
        bottom: 60,
      },
      xAxis: {
        type: 'value',
        min: minMinute,
        max: maxMinute,
        interval: selectedDay === 0 ? 1440 : 120, // 24h intervals for week view, 2h intervals for day view
        splitLine: {
          show: true,
          lineStyle: {
            color: '#E8EEF2',
            type: 'dashed',
          },
        },
        axisLabel: {
          formatter: (value: number) => {
            const dayIdx = Math.floor(value / 1440);
            const dayMin = value % 1440;
            const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
            const hh = String(Math.floor(dayMin / 60)).padStart(2, '0');
            const mm = String(dayMin % 60).padStart(2, '0');
            if (selectedDay === 0) {
              return dayMin === 0 ? `${days[dayIdx]}\n00:00` : `${hh}:${mm}`;
            }
            return `${hh}:${mm}`;
          },
          color: '#526478',
          fontSize: 10,
        },
      },
      yAxis: {
        type: 'value',
        min: 0,
        max: 120,
        interval: 22.5,
        splitLine: {
          show: true,
          lineStyle: {
            color: '#D5DEE5',
            width: 1,
          },
        },
        axisLabel: {
          formatter: (val: number) => {
            const st = stations.find((s) => Math.abs(s.chainage_km - val) < 2);
            if (st) {
              return `${st.station_name}\n(Km ${st.chainage_km})`;
            }
            return `Km ${val}`;
          },
          color: '#142B3E',
          fontWeight: 600,
          fontSize: 10,
        },
      },
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: 0,
          filterMode: 'filter',
        },
        {
          type: 'slider',
          xAxisIndex: 0,
          bottom: 12,
          height: 20,
          borderColor: '#D5DEE5',
          fillerColor: 'rgba(0, 109, 119, 0.15)',
          handleStyle: {
            color: '#006D77',
          },
          labelFormatter: (val: number) => {
            return formatMinuteToIST(val);
          },
          textStyle: {
            color: '#526478',
            fontSize: 10,
          },
        },
      ],
      series: [
        // Dummy items for legend matching
        { name: 'Civil (ENG)', type: 'custom', renderItem: () => null, data: [], itemStyle: { color: DEPT_COLORS.ENG } },
        { name: 'Electrical (ELE)', type: 'custom', renderItem: () => null, data: [], itemStyle: { color: DEPT_COLORS.ELE } },
        { name: 'S&T (SIG)', type: 'custom', renderItem: () => null, data: [], itemStyle: { color: DEPT_COLORS.SIG } },
        { name: 'Passenger Train', type: 'line', data: [], lineStyle: { color: TRAIN_COLORS.PASSENGER } },
        { name: 'Freight Train', type: 'line', data: [], lineStyle: { color: TRAIN_COLORS.FREIGHT, type: 'dashed' } },

        // Real Train String Paths
        ...trainLineSeries,

        // Maintenance Block Packages (Custom Rectangles)
        {
          type: 'custom',
          name: 'Maintenance Block',
          renderItem: renderMaintenanceBlock,
          data: maintenanceData,
          z: 3,
        },
      ],
    };

    chart.setOption(option, true);

    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [filteredAssignments, filteredOccupations, selectedAssignment, minMinute, maxMinute, selectedDay, stations, segmentBounds]);

  const handleZoomIn = () => {
    if (!chartInstance.current) return;
    chartInstance.current.dispatchAction({
      type: 'dataZoom',
      batch: [{ start: 20, end: 80 }],
    });
  };

  const handleZoomOut = () => {
    if (!chartInstance.current) return;
    chartInstance.current.dispatchAction({
      type: 'dataZoom',
      batch: [{ start: 0, end: 100 }],
    });
  };

  const handleReset = () => {
    if (!chartInstance.current) return;
    chartInstance.current.dispatchAction({
      type: 'dataZoom',
      batch: [{ start: 0, end: 100 }],
    });
    setSelectedDay(0);
    setDirectionFilter('ALL');
    setDepartmentFilter('ALL');
    setShowTrains(true);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', flex: 1, height: '100%', minHeight: '520px' }}>
      {/* Chart Control Toolbar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '8px 16px',
          backgroundColor: 'var(--color-surface-warm)',
          borderBottom: '1px solid var(--color-border)',
          fontSize: '11px',
        }}
      >
        {/* Left Filters: Direction & Department */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-muted)', fontWeight: 600 }}>
            <Filter size={12} />
            <span>Track:</span>
          </div>
          <div style={{ display: 'flex', backgroundColor: '#FFFFFF', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)', overflow: 'hidden' }}>
            {(['ALL', 'UP', 'DOWN'] as const).map((dir) => (
              <button
                key={dir}
                onClick={() => setDirectionFilter(dir)}
                style={{
                  padding: '3px 8px',
                  border: 'none',
                  fontSize: '11px',
                  fontWeight: directionFilter === dir ? 700 : 500,
                  backgroundColor: directionFilter === dir ? 'var(--color-action-tint)' : 'transparent',
                  color: directionFilter === dir ? 'var(--color-action)' : 'var(--color-muted)',
                  cursor: 'pointer',
                }}
              >
                {dir === 'ALL' ? 'Both Tracks' : `${dir} Line`}
              </button>
            ))}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginLeft: '8px', color: 'var(--color-muted)', fontWeight: 600 }}>
            <span>Dept:</span>
          </div>
          <select
            value={departmentFilter}
            onChange={(e) => setDepartmentFilter(e.target.value)}
            style={{
              padding: '3px 8px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-border)',
              fontSize: '11px',
              backgroundColor: '#FFFFFF',
              color: 'var(--color-ink)',
            }}
          >
            <option value="ALL">All Departments</option>
            <option value="ENG">Civil / Track (ENG)</option>
            <option value="ELE">Electrical / OHE (ELE)</option>
            <option value="SIG">Signalling (SIG)</option>
          </select>

          {/* Train Path Toggle */}
          <button
            onClick={() => setShowTrains(!showTrains)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '3px 8px',
              marginLeft: '8px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-border)',
              backgroundColor: showTrains ? 'var(--color-surface)' : 'var(--color-canvas)',
              color: showTrains ? 'var(--color-action)' : 'var(--color-muted)',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            {showTrains ? <Eye size={12} /> : <EyeOff size={12} />}
            <span>{showTrains ? 'Trains Visible' : 'Trains Hidden'}</span>
          </button>
        </div>

        {/* Center / Right: Day Horizon Selector & Zoom Tools */}
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          {/* Day Selector Pills */}
          <div style={{ display: 'flex', backgroundColor: '#FFFFFF', borderRadius: 'var(--radius-sm)', border: '1px solid var(--color-border)', overflow: 'hidden' }}>
            <button
              onClick={() => setSelectedDay(0)}
              style={{
                padding: '3px 8px',
                border: 'none',
                fontSize: '11px',
                fontWeight: selectedDay === 0 ? 700 : 500,
                backgroundColor: selectedDay === 0 ? 'var(--color-action)' : 'transparent',
                color: selectedDay === 0 ? '#FFFFFF' : 'var(--color-muted)',
                cursor: 'pointer',
              }}
            >
              Full Week (7D)
            </button>
            {[1, 2, 3, 4, 5, 6, 7].map((day) => (
              <button
                key={day}
                onClick={() => setSelectedDay(day)}
                style={{
                  padding: '3px 6px',
                  border: 'none',
                  fontSize: '10px',
                  fontWeight: selectedDay === day ? 700 : 500,
                  backgroundColor: selectedDay === day ? 'var(--color-action)' : 'transparent',
                  color: selectedDay === day ? '#FFFFFF' : 'var(--color-muted)',
                  cursor: 'pointer',
                }}
              >
                Day {day}
              </button>
            ))}
          </div>

          {/* Zoom Buttons */}
          <div style={{ display: 'flex', gap: '2px' }}>
            <button
              onClick={handleZoomIn}
              title="Zoom In Time Window"
              style={{
                padding: '4px',
                backgroundColor: '#FFFFFF',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--color-ink)',
                cursor: 'pointer',
              }}
            >
              <ZoomIn size={13} />
            </button>
            <button
              onClick={handleZoomOut}
              title="Zoom Out"
              style={{
                padding: '4px',
                backgroundColor: '#FFFFFF',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--color-ink)',
                cursor: 'pointer',
              }}
            >
              <ZoomOut size={13} />
            </button>
            <button
              onClick={handleReset}
              title="Reset View"
              style={{
                padding: '4px',
                backgroundColor: '#FFFFFF',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--color-ink)',
                cursor: 'pointer',
              }}
            >
              <RotateCcw size={13} />
            </button>
          </div>
        </div>
      </div>

      {/* Main ECharts Canvas */}
      <div
        ref={chartRef}
        style={{
          flex: 1,
          width: '100%',
          minHeight: '480px',
        }}
      />
    </div>
  );
};
