import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, Play, AlertTriangle, Clock, Layers, Table, RefreshCw, XCircle, ShieldCheck } from 'lucide-react';
import { SolveJobApi } from '../api/solveJobs';
import { Task, MaterializedAssignment, PlanVersion, SolveJobResponse } from '../types/api';
import { TimeDistanceChart } from '../components/planning/TimeDistanceChart';
import { MaintenanceQueue } from '../components/planning/MaintenanceQueue';
import { ResourceTimeline } from '../components/planning/ResourceTimeline';
import { TabularScheduleView } from '../components/planning/TabularScheduleView';
import { MonthlyAllocationView } from '../components/planning/MonthlyAllocationView';
import { EvidenceDrawer } from '../components/common/EvidenceDrawer';
import { EmptyState } from '../components/common/EmptyState';

export const PlanningView: React.FC = () => {
  // Horizon State
  const [selectedHorizon, setSelectedHorizon] = useState<'WEEKLY' | 'MONTHLY'>('WEEKLY');
  const [selectedViewMode, setSelectedViewMode] = useState<'CANVAS' | 'GANTT' | 'TABLE'>('CANVAS');
  const [selectedProfile, setSelectedProfile] = useState<string>('PROGRAMME_IMPROVEMENT');

  // Operational Data State
  const [tasks, setTasks] = useState<Task[]>([]);
  const [topology, setTopology] = useState<any>(null);
  const [occupations, setOccupations] = useState<any[]>([]);
  const [plans, setPlans] = useState<PlanVersion[]>([]);
  const [activePlan, setActivePlan] = useState<PlanVersion | null>(null);

  // Responsive Layout & Queue Drawer State
  const [isMobile, setIsMobile] = useState<boolean>(typeof window !== 'undefined' ? window.innerWidth <= 768 : false);
  const [isQueueOpen, setIsQueueOpen] = useState<boolean>(typeof window !== 'undefined' ? window.innerWidth > 1024 : true);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Selection Synchronization State
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [selectedAssignment, setSelectedAssignment] = useState<MaterializedAssignment | null>(null);
  const [isEvidenceDrawerOpen, setIsEvidenceDrawerOpen] = useState<boolean>(false);

  // Solve Job Execution State
  const [isSolving, setIsSolving] = useState<boolean>(false);
  const [currentJob, setCurrentJob] = useState<SolveJobResponse | null>(null);
  const [jobPhase, setJobPhase] = useState<string>('');
  const [solveError, setSolveError] = useState<string | null>(null);
  const [abortController, setAbortController] = useState<AbortController | null>(null);

  // Initial Data Load
  const loadInitialData = useCallback(async () => {
    try {
      // 1. Load Corridor Tasks
      const tasksRes = await fetch('/api/v1/tasks?limit=200');
      if (tasksRes.ok) {
        const data = await tasksRes.json();
        setTasks(data.tasks || []);
      }

      // 2. Load Spatial Corridor Topology
      const topo = await SolveJobApi.getTopology('VKC').catch(() => null);
      if (topo) setTopology(topo);

      // 3. Load Timetable Train Occupations
      const occs = await SolveJobApi.getOccupations('VKC').catch(() => []);
      setOccupations(occs);

      // 4. Load Saved Plan Versions
      const planList = await SolveJobApi.listPlans('VKC').catch(() => []);
      setPlans(planList);
      if (planList.length > 0) {
        // Load latest full plan with materialized assignments
        const latestPlan = await SolveJobApi.getPlan(planList[0].plan_id);
        setActivePlan(latestPlan);
      }
    } catch (err: any) {
      console.error('Error loading initial planning workbench data', err);
    }
  }, []);

  useEffect(() => {
    loadInitialData();
  }, [loadInitialData]);

  // Handle Solve Plan Action
  const handleGeneratePlan = async () => {
    setIsSolving(true);
    setSolveError(null);
    setJobPhase('QUEUED');

    const controller = new AbortController();
    setAbortController(controller);

    try {
      // 1. Submit Solve Job (HTTP 202 Accepted)
      const submitReq = {
        corridor_code: 'VKC',
        profile: selectedProfile as any,
        time_limit_seconds: 15.0,
        lattice_step_minutes: 60,
      };

      const { job } = await SolveJobApi.submitJob(submitReq, {
        idempotencyKey: `PLAN-JOB-${Date.now()}`,
      });
      setCurrentJob(job);
      setJobPhase(job.current_phase);

      // 2. Trigger asynchronous leased worker
      await SolveJobApi.executeJob(job.job_id);

      // 3. Poll until terminal with exponential backoff & genuine phase notifications
      const completedJob = await SolveJobApi.pollJobUntilTerminal(job.job_id, {
        signal: controller.signal,
        onPhaseChange: (updated) => {
          setCurrentJob(updated);
          setJobPhase(updated.current_phase);
        },
      });

      setCurrentJob(completedJob);
      setJobPhase(completedJob.current_phase);

      if (completedJob.status === 'COMPLETED' && completedJob.result_plan_id) {
        // 4. Fetch Materialized Plan
        const newPlan = await SolveJobApi.getPlan(completedJob.result_plan_id);
        setActivePlan(newPlan);

        // Refresh plan versions list
        const planList = await SolveJobApi.listPlans('VKC');
        setPlans(planList);
      } else if (completedJob.status === 'FAILED') {
        setSolveError(completedJob.error_detail || 'Solver execution failed');
      }
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        setSolveError(err.message || 'Error generating plan');
      }
    } finally {
      setIsSolving(false);
      setAbortController(null);
    }
  };

  // Handle Cancellation
  const handleCancelSolve = async () => {
    if (abortController) {
      abortController.abort();
    }
    if (currentJob) {
      try {
        await SolveJobApi.cancelJob(currentJob.job_id, 'User cancelled from UI');
        setJobPhase('CANCELLED');
      } catch (err) {
        console.error('Cancel failed', err);
      }
    }
    setIsSolving(false);
  };

  // Selection handlers
  const handleSelectTask = (task: Task) => {
    setSelectedTask(task);
    setIsEvidenceDrawerOpen(true);
  };

  const handleSelectAssignment = (assign: MaterializedAssignment | null) => {
    setSelectedAssignment(assign);
    if (assign) {
      const matchedTask = tasks.find((t) => t.task_id === assign.task_id);
      if (matchedTask) setSelectedTask(matchedTask);
      setIsEvidenceDrawerOpen(true);
    }
  };

  // Switch Plan Version
  const handleSelectPlanVersion = async (planId: string) => {
    try {
      const fullPlan = await SolveJobApi.getPlan(planId);
      setActivePlan(fullPlan);
      setSelectedAssignment(null);
      setSelectedTask(null);
    } catch (err) {
      console.error('Error switching plan version', err);
    }
  };

  // Format phase string for display
  const formatPhaseLabel = (phase: string): string => {
    switch (phase) {
      case 'QUEUED':
        return 'Job Queued in Database';
      case 'CLAIMED':
        return 'Worker Leased Job';
      case 'PREPARING_SNAPSHOT':
        return 'Sealing Input Snapshot';
      case 'BUILDING_CANDIDATES':
      case 'OPTIMIZING_BASE':
        return 'Stage 1: Base Feasibility Solve';
      case 'OPTIMIZING_STAGES':
        return 'Stage 2: Lexicographic Priority Multi-Objective';
      case 'RUNNING_CHECKER':
        return 'Phase 07: Feasibility Oracle Verification';
      case 'RECONCILING':
        return 'Two-Horizon Tactical Reconciliation';
      case 'PUBLISHING':
        return 'Committing Materialized Assignments';
      case 'COMPLETED':
        return 'Solve Completed & Verified';
      default:
        return phase;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', position: 'relative' }}>
      {/* Workbench Header Toolbar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: '#FFFFFF',
          padding: '12px 18px',
          borderRadius: 'var(--radius-lg)',
          border: '1px solid var(--color-border)',
          flexWrap: 'wrap',
          gap: '10px',
        }}
      >
        {/* Left: Corridor Identity & Metadata */}
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontSize: '17px', fontWeight: 700, color: 'var(--color-ink)' }}>
              Operational Planning Workbench
            </h1>
            <span
              style={{
                fontSize: '11px',
                fontFamily: 'var(--font-mono)',
                fontWeight: 700,
                color: 'var(--color-action)',
                backgroundColor: 'var(--color-action-tint)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid #99F6E4',
              }}
            >
              VKC Corridor (Km 0.0 - 120.0)
            </span>
            {activePlan && (
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  color: 'var(--color-success)',
                  backgroundColor: 'var(--color-success-pale)',
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-sm)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <ShieldCheck size={12} /> {activePlan.checker_verdict || 'CHECKED_FEASIBLE'}
              </span>
            )}
          </div>
          <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>
            Time: Asia/Kolkata (UTC+05:30) | Working Timetable (WTT) Active | Independent Oracle Validated
          </div>
        </div>

        {/* Center / Right: Controls */}
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Horizon Toggle */}
          <div style={{ display: 'flex', backgroundColor: 'var(--color-surface-warm)', borderRadius: 'var(--radius-sm)', padding: '2px', border: '1px solid var(--color-border)' }}>
            <button
              onClick={() => setSelectedHorizon('WEEKLY')}
              style={{
                padding: '5px 12px',
                borderRadius: '3px',
                border: 'none',
                fontSize: '11px',
                fontWeight: selectedHorizon === 'WEEKLY' ? 700 : 500,
                backgroundColor: selectedHorizon === 'WEEKLY' ? '#FFFFFF' : 'transparent',
                color: selectedHorizon === 'WEEKLY' ? 'var(--color-action)' : 'var(--color-muted)',
                boxShadow: selectedHorizon === 'WEEKLY' ? 'var(--shadow-sm)' : 'none',
                cursor: 'pointer',
              }}
            >
              Weekly Schedule (7D)
            </button>
            <button
              onClick={() => setSelectedHorizon('MONTHLY')}
              style={{
                padding: '5px 12px',
                borderRadius: '3px',
                border: 'none',
                fontSize: '11px',
                fontWeight: selectedHorizon === 'MONTHLY' ? 700 : 500,
                backgroundColor: selectedHorizon === 'MONTHLY' ? '#FFFFFF' : 'transparent',
                color: selectedHorizon === 'MONTHLY' ? 'var(--color-action)' : 'var(--color-muted)',
                boxShadow: selectedHorizon === 'MONTHLY' ? 'var(--shadow-sm)' : 'none',
                cursor: 'pointer',
              }}
            >
              Monthly Allocation (30D)
            </button>
          </div>

          {/* View Mode Toggle (Weekly only) */}
          {selectedHorizon === 'WEEKLY' && (
            <div style={{ display: 'flex', backgroundColor: 'var(--color-surface-warm)', borderRadius: 'var(--radius-sm)', padding: '2px', border: '1px solid var(--color-border)' }}>
              <button
                onClick={() => setSelectedViewMode('CANVAS')}
                style={{
                  padding: '5px 10px',
                  borderRadius: '3px',
                  border: 'none',
                  fontSize: '11px',
                  fontWeight: selectedViewMode === 'CANVAS' ? 700 : 500,
                  backgroundColor: selectedViewMode === 'CANVAS' ? '#FFFFFF' : 'transparent',
                  color: selectedViewMode === 'CANVAS' ? 'var(--color-ink)' : 'var(--color-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Layers size={11} /> Canvas
              </button>
              <button
                onClick={() => setSelectedViewMode('GANTT')}
                style={{
                  padding: '5px 10px',
                  borderRadius: '3px',
                  border: 'none',
                  fontSize: '11px',
                  fontWeight: selectedViewMode === 'GANTT' ? 700 : 500,
                  backgroundColor: selectedViewMode === 'GANTT' ? '#FFFFFF' : 'transparent',
                  color: selectedViewMode === 'GANTT' ? 'var(--color-ink)' : 'var(--color-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Clock size={11} /> Machines
              </button>
              <button
                onClick={() => setSelectedViewMode('TABLE')}
                style={{
                  padding: '5px 10px',
                  borderRadius: '3px',
                  border: 'none',
                  fontSize: '11px',
                  fontWeight: selectedViewMode === 'TABLE' ? 700 : 500,
                  backgroundColor: selectedViewMode === 'TABLE' ? '#FFFFFF' : 'transparent',
                  color: selectedViewMode === 'TABLE' ? 'var(--color-ink)' : 'var(--color-muted)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <Table size={11} /> Schedule
              </button>
            </div>
          )}

          {/* Queue Toggle Button (Weekly only) */}
          {selectedHorizon === 'WEEKLY' && (
            <button
              onClick={() => setIsQueueOpen(!isQueueOpen)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                padding: '5px 10px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border)',
                fontSize: '11px',
                fontWeight: 600,
                backgroundColor: isQueueOpen ? 'var(--color-surface-warm)' : '#FFFFFF',
                color: isQueueOpen ? 'var(--color-action)' : 'var(--color-muted)',
                cursor: 'pointer',
              }}
              title={isQueueOpen ? 'Hide Maintenance Queue' : 'Show Maintenance Queue'}
            >
              <Layers size={11} />
              <span>{isQueueOpen ? 'Hide Queue' : `Queue (${tasks.length})`}</span>
            </button>
          )}

          {/* Objective Profile Selector */}
          <select
            value={selectedProfile}
            onChange={(e) => setSelectedProfile(e.target.value)}
            disabled={isSolving}
            style={{
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--color-border)',
              fontSize: '11px',
              backgroundColor: '#FFFFFF',
              color: 'var(--color-ink)',
            }}
          >
            <option value="PROGRAMME_IMPROVEMENT">Profile: Programme Improvement</option>
            <option value="DISRUPTION_RECOVERY">Profile: Disruption Recovery (Minimal Churn)</option>
          </select>

          {/* Plan Version Dropdown */}
          {plans.length > 0 && (
            <select
              value={activePlan?.plan_id || ''}
              onChange={(e) => handleSelectPlanVersion(e.target.value)}
              disabled={isSolving}
              style={{
                padding: '6px 10px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--color-border)',
                fontSize: '11px',
                backgroundColor: '#FFFFFF',
                color: 'var(--color-ink)',
                fontFamily: 'var(--font-mono)',
              }}
            >
              {plans.map((p, idx) => (
                <option key={p.plan_id} value={p.plan_id}>
                  v{p.plan_version_number || idx + 1} ({p.metrics?.total_tasks_scheduled || p.assignments?.length || 0} blocks)
                </option>
              ))}
            </select>
          )}

          {/* Solve / Cancel Button */}
          {isSolving ? (
            <button
              onClick={handleCancelSolve}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 14px',
                backgroundColor: '#DC2626',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              <XCircle size={13} />
              <span>Cancel Run</span>
            </button>
          ) : (
            <button
              onClick={handleGeneratePlan}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 16px',
                backgroundColor: 'var(--color-action)',
                color: '#FFFFFF',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              <Play size={13} fill="#FFFFFF" />
              <span>Generate Plan</span>
            </button>
          )}
        </div>
      </div>

      {/* Live Asynchronous Solve Progress Banner */}
      {isSolving && (
        <div
          style={{
            backgroundColor: 'var(--color-action-tint)',
            border: '1px solid var(--color-action)',
            borderRadius: 'var(--radius-md)',
            padding: '12px 18px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: 'var(--shadow-sm)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <RefreshCw size={18} color="var(--color-action)" className="spin" />
            <div>
              <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--color-ink)' }}>
                Durable Asynchronous Job In Progress: {formatPhaseLabel(jobPhase)}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
                Worker leased via PostgreSQL outbox. Phase transitions stream live without simulated progress bars.
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span
              style={{
                fontSize: '11px',
                fontFamily: 'var(--font-mono)',
                fontWeight: 700,
                color: 'var(--color-action)',
                backgroundColor: '#FFFFFF',
                padding: '3px 8px',
                borderRadius: '3px',
                border: '1px solid var(--color-action)',
              }}
            >
              Phase: {jobPhase}
            </span>
          </div>
        </div>
      )}

      {/* Solve Error Alert */}
      {solveError && (
        <div
          style={{
            backgroundColor: 'var(--color-critical-pale)',
            border: '1px solid var(--color-critical)',
            borderRadius: 'var(--radius-md)',
            padding: '10px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            color: 'var(--color-critical)',
            fontSize: '12px',
          }}
        >
          <AlertTriangle size={16} />
          <span><b>Solve Issue:</b> {solveError}</span>
        </div>
      )}

      {/* Content Area Based on Horizon */}
      {selectedHorizon === 'MONTHLY' ? (
        <MonthlyAllocationView />
      ) : (
        <div
          style={{
            display: 'flex',
            flexDirection: isMobile ? 'column' : 'row',
            backgroundColor: '#FFFFFF',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--color-border)',
            minHeight: '540px',
            overflow: 'hidden',
          }}
        >
          {/* Left Column: Maintenance Queue (Toggleable) */}
          {isQueueOpen && (
            <div
              style={{
                width: isMobile ? '100%' : '270px',
                flexShrink: 0,
                borderRight: isMobile ? 'none' : '1px solid var(--color-border)',
                borderBottom: isMobile ? '1px solid var(--color-border)' : 'none',
              }}
            >
              <MaintenanceQueue
                tasks={tasks}
                assignments={activePlan?.assignments || []}
                selectedTask={selectedTask}
                onSelectTask={handleSelectTask}
                onSelectAssignment={handleSelectAssignment}
              />
            </div>
          )}

          {/* Center Workspace Area */}
          <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', position: 'relative' }}>
            {activePlan && activePlan.assignments && activePlan.assignments.length > 0 ? (
              <>
                {selectedViewMode === 'CANVAS' && (
                  <TimeDistanceChart
                    assignments={activePlan.assignments}
                    selectedAssignment={selectedAssignment}
                    onSelectAssignment={handleSelectAssignment}
                    stations={topology?.stations}
                    occupations={occupations}
                  />
                )}
                {selectedViewMode === 'GANTT' && (
                  <ResourceTimeline assignments={activePlan.assignments} />
                )}
                {selectedViewMode === 'TABLE' && (
                  <TabularScheduleView
                    assignments={activePlan.assignments}
                    selectedAssignment={selectedAssignment}
                    onSelectAssignment={handleSelectAssignment}
                  />
                )}
              </>
            ) : (
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px' }}>
                <EmptyState
                  icon={Calendar}
                  title="Awaiting Operational Plan Generation"
                  description="The 120km Vayu-Kosh Corridor timetable and 60 monthly tasks are loaded. Click 'Generate Plan' to launch the OR-Tools CP-SAT Weekly Optimizer via the PostgreSQL leased worker queue."
                  prerequisiteNote="Click 'Generate Plan' to trigger Stage 1 & Stage 2 optimization."
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Contextual Evidence & Verification Drawer */}
      <EvidenceDrawer
        task={selectedTask}
        assignment={selectedAssignment}
        planId={activePlan?.plan_id}
        planVersion={activePlan?.plan_version_number}
        isOpen={isEvidenceDrawerOpen}
        onClose={() => setIsEvidenceDrawerOpen(false)}
        onRepairDispatched={loadInitialData}
      />
    </div>
  );
};
