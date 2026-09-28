import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  Wrench,
  CalendarDays,
  GitCompare,
  ShieldCheck,
  Database,
  FileText,
  CheckCircle2,
  AlertTriangle,
  UserCheck,
  LogOut,
  KeyRound,
  Scale,
  FileCheck,
  Menu,
  X,
  ChevronLeft,
  ChevronRight,
  Radio,
} from 'lucide-react';
import { HealthResponse, SessionResponse } from '../types/api';

interface AppShellProps {
  children?: React.ReactNode;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export const AppShell: React.FC<AppShellProps> = ({ children, activeTab, onTabChange }) => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [session, setSession] = useState<SessionResponse | null>(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [usernameInput, setUsernameInput] = useState('reviewer_operating');
  const [passwordInput, setPasswordInput] = useState('rev@pass2026');
  const [authError, setAuthError] = useState<string | null>(null);

  // Responsive state
  const [windowWidth, setWindowWidth] = useState<number>(
    typeof window !== 'undefined' ? window.innerWidth : 1280
  );
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState<boolean>(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState<boolean>(false);

  const isMobile = windowWidth <= 768;
  const isTablet = windowWidth > 768 && windowWidth <= 1024;

  useEffect(() => {
    const handleResize = () => {
      const w = window.innerWidth;
      setWindowWidth(w);
      if (w > 768) {
        setIsMobileMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Keyboard accessibility: Escape closes modal and mobile menu
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (showLoginModal) setShowLoginModal(false);
        if (isMobileMenuOpen) setIsMobileMenuOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [showLoginModal, isMobileMenuOpen]);

  const fetchSession = () => {
    fetch('/api/v1/auth/session')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setSession(data))
      .catch(() => setSession(null));
  };

  useEffect(() => {
    fetch('/api/v1/health')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setHealth(data))
      .catch(() => setHealth(null));

    fetchSession();
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: usernameInput, password: passwordInput }),
      });
      if (res.ok) {
        const data = await res.json();
        setSession(data);
        setShowLoginModal(false);
      } else {
        const err = await res.json();
        setAuthError(err.detail || 'Login failed');
      }
    } catch {
      setAuthError('Connection error during authentication');
    }
  };

  const handleLogout = async () => {
    await fetch('/api/v1/auth/logout', { method: 'POST' });
    setSession(null);
  };

  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'maintenance', label: 'Maintenance Queue', icon: Wrench },
    { id: 'planning', label: 'Planning Workbench', icon: CalendarDays },
    { id: 'change-review', label: 'PlanDiff & Recovery', icon: GitCompare },
    { id: 'field-reporter', label: 'Live Field Reporter', icon: Radio },
    { id: 'evaluation', label: 'Evaluation & Benchmarks', icon: Scale },
    { id: 'approval', label: 'Programme Approval', icon: FileCheck },
    { id: 'rules', label: 'Rules & Readiness', icon: ShieldCheck },
    { id: 'data', label: 'Data & Outcomes', icon: Database },
    { id: 'audit', label: 'Audit & History', icon: FileText },
    { id: 'gallery', label: 'UI Fixture Gallery', icon: ShieldCheck },
  ];

  const handleNavClick = (tabId: string) => {
    onTabChange(tabId);
    if (isMobile) {
      setIsMobileMenuOpen(false);
    }
  };

  const effectiveSidebarWidth = isMobile
    ? isMobileMenuOpen
      ? '260px'
      : '0px'
    : isSidebarCollapsed || isTablet
    ? '64px'
    : '230px';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', width: '100vw', overflow: 'hidden' }}>
      {/* Skip to Main Content Link for Keyboard / Screen Reader Accessibility */}
      <a href="#main-content" className="skip-link">
        Skip to main content
      </a>

      {/* Top Persistent Context Bar */}
      <header
        role="banner"
        style={{
          height: '52px',
          backgroundColor: 'var(--color-ink)',
          color: '#FFFFFF',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: isMobile ? '0 12px' : '0 20px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          flexShrink: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: isMobile ? '10px' : '16px' }}>
          {/* Mobile Hamburger Button */}
          {isMobile && (
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              aria-label={isMobileMenuOpen ? 'Close Navigation Menu' : 'Open Navigation Menu'}
              aria-expanded={isMobileMenuOpen}
              style={{
                background: 'none',
                border: 'none',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '6px',
                cursor: 'pointer',
              }}
            >
              {isMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          )}

          {/* SAMARATH Parallel Track & Branch SVG Mark */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <svg width="26" height="26" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
              <line x1="4" y1="8" x2="28" y2="8" stroke="#006D77" strokeWidth="2.5" strokeLinecap="round" />
              <line x1="4" y1="24" x2="28" y2="24" stroke="#006D77" strokeWidth="2.5" strokeLinecap="round" />
              <line x1="8" y1="6" x2="8" y2="26" stroke="#526478" strokeWidth="1.5" />
              <line x1="16" y1="6" x2="16" y2="26" stroke="#526478" strokeWidth="1.5" />
              <line x1="24" y1="6" x2="24" y2="26" stroke="#526478" strokeWidth="1.5" />
              <path d="M8 24 C14 24, 18 8, 28 8" stroke="#EAB308" strokeWidth="2.5" strokeLinecap="round" />
            </svg>

            <div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                <span style={{ fontSize: isMobile ? '15px' : '16px', fontWeight: 700, letterSpacing: '0.5px' }}>SAMARATH</span>
                {!isMobile && <span style={{ fontSize: '11px', color: '#f59e0b', fontWeight: 600 }}>SIH 2026 • PS 26027</span>}
              </div>
              {!isMobile && <div style={{ fontSize: '10px', color: '#94A3B8' }}>Ministry of Railways | Transportation & Logistics</div>}
            </div>
          </div>
        </div>

        {/* Operational Context Badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: isMobile ? '8px' : '14px', fontSize: '12px' }}>
          {/* Corridor Badge */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              background: 'rgba(255,255,255,0.06)',
              padding: '4px 8px',
              borderRadius: '4px',
            }}
          >
            <span style={{ color: '#94A3B8', display: isMobile ? 'none' : 'inline' }}>Corridor:</span>
            <strong style={{ color: '#E2E8F0', fontSize: '11px' }}>{isMobile ? 'VKC' : 'Vayu-Kosh (VKC)'}</strong>
          </div>

          {/* Horizon Badge */}
          {!isMobile && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.06)', padding: '4px 10px', borderRadius: '4px' }}>
              <span style={{ color: '#94A3B8' }}>Horizon:</span>
              <strong style={{ color: '#E2E8F0' }}>{isTablet ? 'W42' : 'Week 42 (12-18 Oct 2026)'}</strong>
            </div>
          )}

          {/* Strict Provenance Badge */}
          <div
            style={{
              padding: '2px 6px',
              backgroundColor: 'var(--color-warning-pale)',
              color: 'var(--color-warning)',
              border: '1px solid var(--color-warning)',
              borderRadius: '4px',
              fontWeight: 700,
              fontSize: '10px',
              letterSpacing: '0.5px',
              whiteSpace: 'nowrap',
            }}
          >
            [TEST MODE]
          </div>

          {/* Process & DB Health */}
          {!isMobile && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              {health?.database.connected ? (
                <span style={{ color: '#4ADE80', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}>
                  <CheckCircle2 size={13} /> {isTablet ? 'DB OK' : `DB: ${health.database.engine} (${health.database.latency_ms}ms)`}
                </span>
              ) : (
                <span style={{ color: '#F87171', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '11px' }}>
                  <AlertTriangle size={13} /> {health?.status === 'degraded' ? 'DB Degraded' : 'Connecting...'}
                </span>
              )}
            </div>
          )}

          {/* Authenticated Identity Pill */}
          {session ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(0,109,119,0.3)', padding: '3px 8px', borderRadius: '4px', border: '1px solid #006D77' }}>
              <UserCheck size={14} color="#5EEAD4" />
              <span style={{ fontSize: '11px', color: '#E2E8F0', fontWeight: 600, maxWidth: isMobile ? '80px' : '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {session.display_name}
              </span>
              <button
                onClick={handleLogout}
                title="Logout"
                aria-label="Logout"
                style={{ background: 'none', border: 'none', color: '#94A3B8', display: 'flex', alignItems: 'center', padding: '2px', cursor: 'pointer' }}
              >
                <LogOut size={13} />
              </button>
            </div>
          ) : (
            <button
              onClick={() => setShowLoginModal(true)}
              aria-label="Login"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '4px 10px',
                backgroundColor: 'var(--color-action)',
                color: '#FFFFFF',
                borderRadius: '4px',
                border: 'none',
                fontSize: '11px',
                fontWeight: 600,
              }}
            >
              <KeyRound size={13} />
              <span>Login</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', position: 'relative' }}>
        {/* Mobile Backdrop Overlay */}
        {isMobile && isMobileMenuOpen && (
          <div
            onClick={() => setIsMobileMenuOpen(false)}
            aria-hidden="true"
            style={{
              position: 'fixed',
              inset: '52px 0 0 0',
              backgroundColor: 'rgba(20, 43, 62, 0.5)',
              zIndex: 90,
            }}
          />
        )}

        {/* Navigation Sidebar */}
        <aside
          role="navigation"
          aria-label="Application Navigation"
          style={{
            width: effectiveSidebarWidth,
            backgroundColor: 'var(--color-surface)',
            borderRight: '1px solid var(--color-border)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            padding: effectiveSidebarWidth === '0px' ? '0' : '12px 8px',
            flexShrink: 0,
            transition: 'width 200ms ease, padding 200ms ease',
            overflowY: 'auto',
            overflowX: 'hidden',
            zIndex: 95,
            ...(isMobile
              ? {
                  position: 'fixed',
                  top: '52px',
                  bottom: 0,
                  left: 0,
                  boxShadow: isMobileMenuOpen ? 'var(--shadow-md)' : 'none',
                }
              : {}),
          }}
        >
          {effectiveSidebarWidth !== '0px' && (
            <>
              <div>
                {/* Desktop Collapse / Expand Toggle */}
                {!isMobile && (
                  <div style={{ display: 'flex', justifyContent: isSidebarCollapsed ? 'center' : 'flex-end', marginBottom: '8px', padding: '0 4px' }}>
                    <button
                      onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
                      title={isSidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
                      aria-label={isSidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
                      style={{
                        background: 'none',
                        border: '1px solid var(--color-border-subtle)',
                        borderRadius: '4px',
                        color: 'var(--color-muted)',
                        padding: '4px 6px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {isSidebarCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
                    </button>
                  </div>
                )}

                <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  {navItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = activeTab === item.id;
                    const isCollapsedMode = !isMobile && (isSidebarCollapsed || isTablet);

                    return (
                      <button
                        key={item.id}
                        onClick={() => handleNavClick(item.id)}
                        title={isCollapsedMode ? item.label : undefined}
                        aria-label={item.label}
                        aria-current={isActive ? 'page' : undefined}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: isCollapsedMode ? 'center' : 'flex-start',
                          gap: '10px',
                          padding: isCollapsedMode ? '10px 0' : '8px 12px',
                          borderRadius: 'var(--radius-md)',
                          border: 'none',
                          backgroundColor: isActive ? 'var(--color-action-tint)' : 'transparent',
                          color: isActive ? 'var(--color-action)' : 'var(--color-muted)',
                          fontWeight: isActive ? 600 : 500,
                          fontSize: '13px',
                          textAlign: 'left',
                          width: '100%',
                          transition: 'all 0.15s ease',
                        }}
                      >
                        <Icon size={18} style={{ flexShrink: 0 }} />
                        {!isCollapsedMode && <span style={{ whiteSpace: 'nowrap' }}>{item.label}</span>}
                      </button>
                    );
                  })}
                </nav>
              </div>

              {/* Bottom Context Pill */}
              {(!isSidebarCollapsed && !isTablet) || isMobile ? (
                <div
                  style={{
                    padding: '10px',
                    backgroundColor: 'var(--color-surface-warm)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--color-border-subtle)',
                    fontSize: '11px',
                    color: 'var(--color-muted)',
                    marginTop: '16px',
                  }}
                >
                  <div>Role: <strong>{session ? session.roles.join(', ') : 'Not Logged In'}</strong></div>
                  <div>Department: <strong>{session?.department || 'ALL / Operating'}</strong></div>
                  <div>Territory: <strong>{session?.territory || 'VKC'}</strong></div>
                </div>
              ) : null}
            </>
          )}
        </aside>

        {/* Content Area */}
        <main
          id="main-content"
          role="main"
          tabIndex={-1}
          style={{
            flex: 1,
            overflowY: 'auto',
            overflowX: 'hidden',
            backgroundColor: 'var(--color-canvas)',
            padding: isMobile ? '12px' : '20px',
            outline: 'none',
          }}
        >
          <div style={{ maxWidth: '1440px', margin: '0 auto', width: '100%' }}>
            {children}
          </div>
        </main>
      </div>

      {/* Login Modal */}
      {showLoginModal && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(20,43,62,0.6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
          onClick={() => setShowLoginModal(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="login-dialog-title"
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: 'var(--radius-lg)',
              padding: '24px',
              width: '90%',
              maxWidth: '380px',
              boxShadow: 'var(--shadow-md)',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 id="login-dialog-title" style={{ fontSize: '16px', fontWeight: 700, marginBottom: '8px' }}>
              Authenticate Identity
            </h2>
            <p style={{ fontSize: '12px', color: 'var(--color-muted)', marginBottom: '16px' }}>
              Select a bootstrap role for evaluation and testing.
            </p>

            {authError && (
              <div style={{ padding: '8px', backgroundColor: 'var(--color-critical-pale)', color: 'var(--color-critical)', borderRadius: '4px', fontSize: '12px', marginBottom: '12px' }}>
                {authError}
              </div>
            )}

            <form onSubmit={handleLogin}>
              <div style={{ marginBottom: '12px' }}>
                <label style={{ fontSize: '11px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Role / Username</label>
                <select
                  value={usernameInput}
                  onChange={(e) => {
                    setUsernameInput(e.target.value);
                    if (e.target.value === 'planner_tms') setPasswordInput('tms@pass2026');
                    else if (e.target.value === 'planner_smms') setPasswordInput('smms@pass2026');
                    else if (e.target.value === 'planner_tdms') setPasswordInput('tdms@pass2026');
                    else if (e.target.value === 'approver_operating') setPasswordInput('appr@pass2026');
                    else if (e.target.value === 'reviewer_operating') setPasswordInput('rev@pass2026');
                    else if (e.target.value === 'admin_infra') setPasswordInput('admin@pass2026');
                  }}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '13px' }}
                >
                  <option value="reviewer_operating">reviewer_operating (Operating Reviewer)</option>
                  <option value="approver_operating">approver_operating (Sr. DOM / Approver)</option>
                  <option value="planner_tms">planner_tms (Track / P-Way Planner)</option>
                  <option value="planner_smms">planner_smms (S&T / Signalling Planner)</option>
                  <option value="planner_tdms">planner_tdms (TRD / OHE Planner)</option>
                  <option value="admin_infra">admin_infra (Infrastructure Admin)</option>
                </select>
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ fontSize: '11px', fontWeight: 600, display: 'block', marginBottom: '4px' }}>Password</label>
                <input
                  type="password"
                  value={passwordInput}
                  onChange={(e) => setPasswordInput(e.target.value)}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '13px' }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                <button
                  type="button"
                  onClick={() => setShowLoginModal(false)}
                  style={{ padding: '8px 14px', borderRadius: '4px', border: '1px solid var(--color-border)', backgroundColor: '#FFFFFF', fontSize: '12px' }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  style={{ padding: '8px 16px', borderRadius: '4px', border: 'none', backgroundColor: 'var(--color-action)', color: '#FFFFFF', fontWeight: 600, fontSize: '12px' }}
                >
                  Sign In
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
