import React, { useState, useEffect } from 'react';
import {
  Upload,
  Lock,
  CheckCircle2,
  Copy,
  Trash2,
  ExternalLink,
  ShieldAlert,
  Check,
} from 'lucide-react';
import { ProvenanceBadge } from '../components/common/ProvenanceBadge';
import { ExecutionOutcomesPanel } from '../components/outcomes/ExecutionOutcomesPanel';

export const DataView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'outcomes' | 'manifest' | 'ingest' | 'quarantine' | 'snapshots' | 'fixtures'>('outcomes');

  // Ingestion tab state
  const [importText, setImportText] = useState<string>('');
  const [isDryRun, setIsDryRun] = useState<boolean>(true);
  const [importFormat, setImportFormat] = useState<'json' | 'csv'>('json');
  const [importResult, setImportResult] = useState<any>(null);
  const [isImporting, setIsImporting] = useState<boolean>(false);
  const [importError, setImportError] = useState<string | null>(null);

  // Quarantine state
  const [quarantineItems, setQuarantineItems] = useState<any[]>([]);
  const [loadingQuarantine, setLoadingQuarantine] = useState<boolean>(false);

  // Snapshots state
  const [snapshots, setSnapshots] = useState<any[]>([]);
  const [loadingSnapshots, setLoadingSnapshots] = useState<boolean>(false);
  const [isSealing, setIsSealing] = useState<boolean>(false);
  const [copiedHash, setCopiedHash] = useState<string | null>(null);

  // Fixtures state
  const [fixtures, setFixtures] = useState<any>({});
  const [loadingFixtures, setLoadingFixtures] = useState<boolean>(false);

  // External sync state
  const [externalSyncStatus, setExternalSyncStatus] = useState<any>(null);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);

  const fetchQuarantine = async () => {
    setLoadingQuarantine(true);
    try {
      const res = await fetch('/api/v1/gateway/quarantine');
      if (res.ok) {
        const data = await res.json();
        setQuarantineItems(data.items || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingQuarantine(false);
    }
  };

  const fetchSnapshots = async () => {
    setLoadingSnapshots(true);
    try {
      const res = await fetch('/api/v1/gateway/snapshots');
      if (res.ok) {
        const data = await res.json();
        setSnapshots(data.snapshots || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSnapshots(false);
    }
  };

  const fetchFixtures = async () => {
    setLoadingFixtures(true);
    try {
      const res = await fetch('/api/v1/gateway/fixtures');
      if (res.ok) {
        const data = await res.json();
        setFixtures(data.fixtures || {});
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingFixtures(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'quarantine') fetchQuarantine();
    if (activeTab === 'snapshots') fetchSnapshots();
    if (activeTab === 'fixtures') fetchFixtures();
  }, [activeTab]);

  const handleRunImport = async () => {
    if (!importText.trim()) {
      setImportError('Please provide CSV or JSON data to import.');
      return;
    }
    setIsImporting(true);
    setImportError(null);
    setImportResult(null);

    try {
      const res = await fetch(`/api/v1/gateway/import?dry_run=${isDryRun}&format_type=${importFormat}`, {
        method: 'POST',
        headers: { 'Content-Type': importFormat === 'csv' ? 'text/csv' : 'application/json' },
        body: importText,
      });

      const data = await res.json();
      if (!res.ok) {
        setImportError(data.detail || `Import failed with HTTP ${res.status}`);
      } else {
        setImportResult(data);
      }
    } catch (err: any) {
      setImportError(err.message || 'Import failed');
    } finally {
      setIsImporting(false);
    }
  };

  const handleSealSnapshot = async () => {
    setIsSealing(true);
    try {
      const res = await fetch('/api/v1/gateway/snapshots/seal?corridor_code=VKC', { method: 'POST' });
      if (res.ok) {
        await fetchSnapshots();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsSealing(false);
    }
  };

  const handleExternalSync = async () => {
    setIsSyncing(true);
    setExternalSyncStatus(null);
    try {
      const res = await fetch('/api/v1/gateway/external/sync', { method: 'POST' });
      const data = await res.json();
      setExternalSyncStatus(data);
    } catch (e: any) {
      setExternalSyncStatus({ detail: e.message });
    } finally {
      setIsSyncing(false);
    }
  };

  const handleDismissQuarantine = async (id: string) => {
    try {
      await fetch(`/api/v1/gateway/quarantine/${id}`, { method: 'DELETE' });
      await fetchQuarantine();
    } catch (e) {
      console.error(e);
    }
  };

  const handleClearAllQuarantine = async () => {
    try {
      await fetch('/api/v1/gateway/quarantine/clear', { method: 'POST' });
      await fetchQuarantine();
    } catch (e) {
      console.error(e);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedHash(text);
    setTimeout(() => setCopiedHash(null), 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Top Header */}
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
              Data Ingestion, Quarantine & Provenance Gateway
            </h1>
            <ProvenanceBadge mode="TEST" />
          </div>
          <div style={{ fontSize: '12px', color: 'var(--color-muted)', marginTop: '2px' }}>
            Shared adapter contract, RFC 7807 isolation store, canonical SHA-256 snapshots, and hand-checkable fixtures
          </div>
        </div>

        <button
          onClick={handleExternalSync}
          disabled={isSyncing}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '8px 12px',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--color-border)',
            backgroundColor: 'var(--color-surface-warm)',
            color: 'var(--color-ink)',
            fontSize: '12px',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <ExternalLink size={14} />
          <span>Test Live Authority Sync</span>
        </button>
      </div>

      {externalSyncStatus && (
        <div
          style={{
            backgroundColor: 'rgba(148, 98, 0, 0.08)',
            border: '1px solid var(--color-warning)',
            borderRadius: 'var(--radius-md)',
            padding: '14px 16px',
            fontSize: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-warning)', fontWeight: 700, marginBottom: '4px' }}>
            <ShieldAlert size={16} />
            <span>Honest Evaluation: {externalSyncStatus.title || 'HTTP 501 Not Implemented'}</span>
          </div>
          <div style={{ color: 'var(--color-ink)', lineHeight: 1.5 }}>
            {externalSyncStatus.detail}
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '4px', borderBottom: '1px solid var(--color-border)', paddingBottom: '2px' }}>
        {[
          { id: 'outcomes', label: 'Execution Feedback & Outcomes' },
          { id: 'manifest', label: 'Corridor Manifest & Topology' },
          { id: 'ingest', label: 'CSV / JSON Ingestion' },
          { id: 'quarantine', label: `Quarantine Store (${quarantineItems.length})` },
          { id: 'snapshots', label: `Sealed Snapshots (${snapshots.length})` },
          { id: 'fixtures', label: '8 Hand-Checkable Fixtures' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            style={{
              padding: '8px 16px',
              border: 'none',
              borderBottom: activeTab === tab.id ? '2px solid var(--color-action)' : '2px solid transparent',
              backgroundColor: 'transparent',
              color: activeTab === tab.id ? 'var(--color-action)' : 'var(--color-muted)',
              fontSize: '13px',
              fontWeight: activeTab === tab.id ? 700 : 500,
              cursor: 'pointer',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab 0: Execution Feedback & Outcomes */}
      {activeTab === 'outcomes' && (
        <ExecutionOutcomesPanel />
      )}

      {/* Tab 1: Corridor Manifest & Topology */}
      {activeTab === 'manifest' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
            <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600 }}>CORRIDOR SCOPE</div>
              <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>VKC (120 Km)</div>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>Vayu-Kosh Corridor</div>
            </div>

            <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600 }}>STATIONS & TRACKS</div>
              <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>6 Stations / 10 Segs</div>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>ALP, BRV, CHR, DLT, ECH, FXT</div>
            </div>

            <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600 }}>TRAFFIC DENSITY</div>
              <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>40 Daily Trains</div>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>Express, Passenger & Freight</div>
            </div>

            <div style={{ padding: '16px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', fontWeight: 600 }}>POWER ISOLATION</div>
              <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>6 Elementary Secs</div>
              <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '2px' }}>Neutral section at CHR (Km 48.0)</div>
            </div>
          </div>

          <div style={{ backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', padding: '20px' }}>
            <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '8px' }}>Station Chainage and Crossover Spine</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px', marginTop: '16px' }}>
              {[
                { code: 'ALP', name: 'Alpha', km: '0.0', lines: 4, xover: 'Yes' },
                { code: 'BRV', name: 'Bravo', km: '22.5', lines: 3, xover: 'Yes' },
                { code: 'CHR', name: 'Charlie', km: '48.0', lines: 4, xover: 'Yes (Neutral)' },
                { code: 'DLT', name: 'Delta', km: '73.2', lines: 3, xover: 'Yes' },
                { code: 'ECH', name: 'Echo', km: '96.8', lines: 2, xover: 'No' },
                { code: 'FXT', name: 'Foxtrot', km: '120.0', lines: 4, xover: 'Yes' },
              ].map((s) => (
                <div key={s.code} style={{ padding: '12px', backgroundColor: 'var(--color-canvas)', borderRadius: '6px', border: '1px solid var(--color-border)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--color-action)' }}>{s.code}</span>
                    <span style={{ fontSize: '10px', color: 'var(--color-muted)' }}>Km {s.km}</span>
                  </div>
                  <div style={{ fontSize: '12px', fontWeight: 600, marginTop: '4px' }}>{s.name}</div>
                  <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '6px' }}>{s.lines} Lines | Xover: {s.xover}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: CSV / JSON Ingestion */}
      {activeTab === 'ingest' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <label style={{ fontSize: '12px', fontWeight: 600 }}>Format:</label>
              <select
                value={importFormat}
                onChange={(e) => setImportFormat(e.target.value as any)}
                style={{ padding: '4px 8px', borderRadius: '4px', border: '1px solid var(--color-border)', fontSize: '12px' }}
              >
                <option value="json">JSON (Array of Records)</option>
                <option value="csv">CSV (Comma-Separated Values)</option>
              </select>

              <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', cursor: 'pointer', marginLeft: '12px' }}>
                <input
                  type="checkbox"
                  checked={isDryRun}
                  onChange={(e) => setIsDryRun(e.target.checked)}
                />
                <span style={{ fontWeight: 600 }}>Dry Run (Validation Only - Do Not Commit to DB)</span>
              </label>
            </div>

            <button
              onClick={() => {
                if (importFormat === 'csv') {
                  setImportText(
                    `business_key,department,sub_department,work_type,description,station_from,station_to,track_segment_id,chainage_start_km,chainage_end_km,duration_minutes,setup_buffer_minutes,restoration_buffer_minutes,criticality,deadline_utc,required_resources,requires_power_block,requires_speed_restriction_after,provenance_mode\nTASK-DEMO-001,ENGINEERING,PWAY,PLAIN_TRACK_TAMPING,Corridor tamping between Alpha and Bravo,ALP,BRV,SEC-01-DN,5.0,8.0,150,30,30,TIER_1_MANDATORY,2026-10-16T18:00:00Z,MACHINE:CSM-01:1,false,false,TEST\nTASK-BAD-ROW,SIGNALLING,S&T,POINT_CHECK,Invalid short duration test,BRV,CHR,SEC-02-UP,24.0,25.0,5,15,15,TIER_3_CYCLIC,2026-10-17T18:00:00Z,,false,false,TEST`
                  );
                } else {
                  setImportText(
                    JSON.stringify([
                      {
                        business_key: "TASK-DEMO-001",
                        department: "ENGINEERING",
                        sub_department: "PWAY",
                        work_type: "PLAIN_TRACK_TAMPING",
                        description: "Corridor tamping between Alpha and Bravo",
                        station_from: "ALP",
                        station_to: "BRV",
                        track_segment_id: "SEC-01-DN",
                        chainage_start_km: 5.0,
                        chainage_end_km: 8.0,
                        duration_minutes: 150,
                        setup_buffer_minutes: 30,
                        restoration_buffer_minutes: 30,
                        criticality: "TIER_1_MANDATORY",
                        deadline_utc: "2026-10-16T18:00:00Z",
                        required_resources: [{ resource_type: "MACHINE", resource_id: "CSM-01", quantity: 1 }],
                        requires_power_block: false,
                        provenance_mode: "TEST"
                      },
                      {
                        business_key: "TASK-BAD-ROW",
                        department: "SIGNALLING",
                        sub_department: "S&T",
                        work_type: "POINT_CHECK",
                        description: "Invalid short duration test (<15m)",
                        station_from: "BRV",
                        station_to: "CHR",
                        track_segment_id: "SEC-02-UP",
                        chainage_start_km: 24.0,
                        chainage_end_km: 25.0,
                        duration_minutes: 5,
                        criticality: "TIER_3_CYCLIC",
                        deadline_utc: "2026-10-17T18:00:00Z",
                        provenance_mode: "TEST"
                      }
                    ], null, 2)
                  );
                }
              }}
              style={{ fontSize: '11px', color: 'var(--color-action)', background: 'none', border: 'none', cursor: 'pointer', textDecoration: 'underline' }}
            >
              Load Sample Batch (1 Valid + 1 Malformed Row)
            </button>
          </div>

          <textarea
            value={importText}
            onChange={(e) => setImportText(e.target.value)}
            placeholder={importFormat === 'csv' ? 'Paste CSV header and rows here...' : 'Paste JSON array here...'}
            rows={10}
            style={{
              width: '100%',
              padding: '12px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--color-border)',
              fontFamily: 'monospace',
              fontSize: '12px',
              backgroundColor: '#ffffff',
            }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontSize: '11px', color: 'var(--color-muted)' }}>
              Formula Safety: Cells starting with =, @, +, - are automatically neutralized. XLSX is rejected.
            </div>

            <button
              onClick={handleRunImport}
              disabled={isImporting}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '10px 20px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-action)',
                color: '#ffffff',
                border: 'none',
                fontWeight: 600,
                fontSize: '13px',
                cursor: isImporting ? 'not-allowed' : 'pointer',
              }}
            >
              <Upload size={16} />
              <span>{isImporting ? 'Validating...' : isDryRun ? 'Run Validation Dry-Run' : 'Commit Batch to Database'}</span>
            </button>
          </div>

          {importError && (
            <div style={{ backgroundColor: 'rgba(179, 54, 54, 0.08)', border: '1px solid var(--color-critical)', borderRadius: 'var(--radius-md)', padding: '12px', color: 'var(--color-critical)', fontSize: '12px' }}>
              <strong>Import Error:</strong> {importError}
            </div>
          )}

          {importResult && (
            <div style={{ backgroundColor: 'var(--color-surface)', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-md)', padding: '16px' }}>
              <h3 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CheckCircle2 size={16} color="var(--color-action)" />
                <span>Ingestion Invariant Report ({importResult.dry_run ? 'Dry Run Mode' : 'Committed'})</span>
              </h3>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', marginBottom: '16px' }}>
                <div style={{ padding: '10px', backgroundColor: 'var(--color-canvas)', borderRadius: '4px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--color-muted)' }}>Total Records</div>
                  <div style={{ fontSize: '18px', fontWeight: 700 }}>{importResult.total_rows}</div>
                </div>
                <div style={{ padding: '10px', backgroundColor: 'rgba(0, 109, 119, 0.08)', borderRadius: '4px', color: 'var(--color-action)' }}>
                  <div style={{ fontSize: '11px' }}>Accepted Valid Rows</div>
                  <div style={{ fontSize: '18px', fontWeight: 700 }}>{importResult.accepted_count}</div>
                </div>
                <div style={{ padding: '10px', backgroundColor: 'rgba(179, 54, 54, 0.08)', borderRadius: '4px', color: 'var(--color-critical)' }}>
                  <div style={{ fontSize: '11px' }}>Quarantined Rows</div>
                  <div style={{ fontSize: '18px', fontWeight: 700 }}>{importResult.quarantined_count}</div>
                </div>
              </div>

              {importResult.quarantined_items && importResult.quarantined_items.length > 0 && (
                <div>
                  <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-critical)', marginBottom: '6px' }}>
                    Quarantine RFC 7807 Breakdown:
                  </div>
                  {importResult.quarantined_items.map((q: any, idx: number) => (
                    <div key={idx} style={{ padding: '8px 10px', backgroundColor: 'rgba(179, 54, 54, 0.04)', border: '1px solid rgba(179, 54, 54, 0.2)', borderRadius: '4px', fontSize: '11px', marginBottom: '6px' }}>
                      <strong>Row #{q.row_index} ({q.business_key}):</strong> {q.error_type} - {JSON.stringify(q.field_errors || q.error_detail)}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Quarantine Isolation Store */}
      {activeTab === 'quarantine' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontSize: '13px', color: 'var(--color-muted)' }}>
              Isolated malformed rows awaiting human review or field re-submission. Does not pollute operational solving.
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={fetchQuarantine}
                style={{ padding: '6px 12px', borderRadius: '4px', border: '1px solid var(--color-border)', backgroundColor: 'transparent', fontSize: '12px', cursor: 'pointer' }}
              >
                Refresh
              </button>
              {quarantineItems.length > 0 && (
                <button
                  onClick={handleClearAllQuarantine}
                  style={{ padding: '6px 12px', borderRadius: '4px', border: '1px solid var(--color-critical)', backgroundColor: 'transparent', color: 'var(--color-critical)', fontSize: '12px', cursor: 'pointer' }}
                >
                  Clear Quarantine
                </button>
              )}
            </div>
          </div>

          {loadingQuarantine ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-muted)' }}>Loading quarantine records...</div>
          ) : quarantineItems.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <CheckCircle2 size={32} color="var(--color-action)" style={{ margin: '0 auto 12px auto' }} />
              <div style={{ fontSize: '16px', fontWeight: 700 }}>Quarantine Store is Clean</div>
              <div style={{ fontSize: '12px', color: 'var(--color-muted)', marginTop: '4px' }}>No malformed or rejected records currently in quarantine.</div>
            </div>
          ) : (
            <div style={{ backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)', overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                <thead>
                  <tr style={{ backgroundColor: 'var(--color-canvas)', borderBottom: '1px solid var(--color-border)', textAlign: 'left' }}>
                    <th style={{ padding: '10px 14px' }}>Row</th>
                    <th style={{ padding: '10px 14px' }}>Business Key</th>
                    <th style={{ padding: '10px 14px' }}>Error Type</th>
                    <th style={{ padding: '10px 14px' }}>RFC 7807 Validation Details</th>
                    <th style={{ padding: '10px 14px' }}>Timestamp</th>
                    <th style={{ padding: '10px 14px' }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {quarantineItems.map((item) => (
                    <tr key={item.quarantine_id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                      <td style={{ padding: '12px 14px', fontFamily: 'monospace' }}>#{item.row_index}</td>
                      <td style={{ padding: '12px 14px', fontWeight: 600, color: 'var(--color-critical)' }}>{item.business_key}</td>
                      <td style={{ padding: '12px 14px' }}>
                        <span style={{ padding: '2px 6px', borderRadius: '4px', backgroundColor: 'rgba(179, 54, 54, 0.1)', color: 'var(--color-critical)', fontSize: '11px', fontWeight: 600 }}>
                          {item.error_type}
                        </span>
                      </td>
                      <td style={{ padding: '12px 14px', fontSize: '11px', maxWidth: '340px' }}>
                        {item.field_errors ? (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                            {item.field_errors.map((fe: any, fidx: number) => (
                              <div key={fidx}>
                                <strong>{fe.field}:</strong> {fe.error}
                              </div>
                            ))}
                          </div>
                        ) : (
                          item.error_detail
                        )}
                      </td>
                      <td style={{ padding: '12px 14px', fontSize: '11px', color: 'var(--color-muted)' }}>
                        {item.timestamp_utc ? item.timestamp_utc.split('T')[1].slice(0, 8) : 'N/A'}
                      </td>
                      <td style={{ padding: '12px 14px' }}>
                        <button
                          onClick={() => handleDismissQuarantine(item.quarantine_id)}
                          style={{ background: 'none', border: 'none', color: 'var(--color-critical)', cursor: 'pointer', padding: '4px' }}
                          title="Dismiss record"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Sealed Immutable Snapshots */}
      {activeTab === 'snapshots' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ fontSize: '13px', color: 'var(--color-muted)' }}>
              Deterministic content-addressed snapshots. Solvers and validators run against the exact sealed snapshot digest.
            </div>

            <button
              onClick={handleSealSnapshot}
              disabled={isSealing}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 14px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'var(--color-action)',
                color: '#ffffff',
                border: 'none',
                fontWeight: 600,
                fontSize: '12px',
                cursor: isSealing ? 'not-allowed' : 'pointer',
              }}
            >
              <Lock size={14} />
              <span>{isSealing ? 'Sealing...' : 'Seal Snapshot from Current DB'}</span>
            </button>
          </div>

          {loadingSnapshots ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-muted)' }}>Loading snapshots...</div>
          ) : snapshots.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '60px', backgroundColor: 'var(--color-surface)', borderRadius: 'var(--radius-md)', border: '1px solid var(--color-border)' }}>
              <Lock size={32} color="var(--color-muted)" style={{ margin: '0 auto 12px auto' }} />
              <div style={{ fontSize: '16px', fontWeight: 700 }}>No Sealed Snapshots in Database</div>
              <div style={{ fontSize: '12px', color: 'var(--color-muted)', marginTop: '4px' }}>Click "Seal Snapshot from Current DB" to freeze an immutable planning container.</div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {snapshots.map((s) => (
                <div
                  key={s.snapshot_id}
                  style={{
                    backgroundColor: 'var(--color-surface)',
                    borderRadius: 'var(--radius-md)',
                    border: '1px solid var(--color-border)',
                    padding: '16px 20px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--color-ink)' }}>
                        Snapshot {s.corridor_code} ({s.task_count} Tasks)
                      </span>
                      <span style={{ fontSize: '10px', padding: '2px 6px', borderRadius: '4px', backgroundColor: 'rgba(0, 109, 119, 0.1)', color: 'var(--color-action)', fontWeight: 700 }}>
                        IMMUTABLE SEALED
                      </span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px', fontFamily: 'monospace', fontSize: '11px', color: 'var(--color-muted)' }}>
                      <span>Hash:</span>
                      <span style={{ backgroundColor: 'var(--color-canvas)', padding: '2px 6px', borderRadius: '3px', color: 'var(--color-ink)' }}>
                        {s.snapshot_hash}
                      </span>
                      <button
                        onClick={() => copyToClipboard(s.snapshot_hash)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '2px', color: 'var(--color-action)' }}
                        title="Copy canonical hash"
                      >
                        {copiedHash === s.snapshot_hash ? <Check size={12} /> : <Copy size={12} />}
                      </button>
                    </div>

                    <div style={{ fontSize: '11px', color: 'var(--color-muted)', marginTop: '6px' }}>
                      Horizon: {s.horizon_start_utc.slice(0, 10)} to {s.horizon_end_utc.slice(0, 10)} | Sealed by: {s.created_by} at {s.created_at_utc.replace('T', ' ').slice(0, 19)} UTC
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 5: 8 Hand-Checkable Fixtures */}
      {activeTab === 'fixtures' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ fontSize: '13px', color: 'var(--color-muted)' }}>
            8 explicit edge scenarios for Smart India Hackathon jury inspection. Fully hand-verifiable with deterministic hashes.
          </div>

          {loadingFixtures ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-muted)' }}>Loading hand-checkable fixtures...</div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '14px' }}>
              {Object.entries(fixtures).map(([key, f]: [string, any]) => (
              <div
                key={key}
                style={{
                  backgroundColor: 'var(--color-surface)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--color-border)',
                  padding: '16px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--color-ink)' }}>
                    {key.replace(/_/g, ' ').toUpperCase()}
                  </span>
                  <span style={{ fontSize: '10px', padding: '2px 6px', borderRadius: '4px', backgroundColor: 'rgba(148, 98, 0, 0.1)', color: 'var(--color-warning)', fontWeight: 700 }}>
                    {f.provenance_badge}
                  </span>
                </div>

                <div style={{ fontSize: '12px', color: 'var(--color-ink)', marginTop: '8px', lineHeight: 1.4 }}>
                  {f.description}
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px', marginTop: '12px', fontSize: '11px' }}>
                  <div style={{ backgroundColor: 'var(--color-canvas)', padding: '6px 8px', borderRadius: '4px' }}>
                    <span style={{ color: 'var(--color-muted)' }}>Expected Verdict:</span>
                    <div style={{ fontWeight: 700, color: 'var(--color-action)' }}>{f.expected_verdict}</div>
                  </div>

                  <div style={{ backgroundColor: 'var(--color-canvas)', padding: '6px 8px', borderRadius: '4px' }}>
                    <span style={{ color: 'var(--color-muted)' }}>Fixture Hash:</span>
                    <div style={{ fontWeight: 700, fontFamily: 'monospace' }}>{f.fixture_hash}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          )}
        </div>
      )}
    </div>
  );
};
