# SAMARATH: 3-Minute Live Demonstration Script & Evaluator Challenge Protocol

**Problem Statement:** SIH26027 (Ministry of Railways, Smart India Hackathon 2026)  
**Corridor:** Vayu-Kosh Corridor (VKC Km 0.0 – 120.0, 10 Stations)  
**Theme:** "Signal & Slate" — Deterministic AI Operational Workbench  
**Total Demonstration Time:** Exactly 3 Minutes (180 Seconds)  
**System Verification Mode:** 100% Offline Air-Gapped Laptop Demonstration  

---

## 1. Timing Breakdown & Presenter Narration

```
0:00 ──────────────── 0:35 ──────────────── 1:15 ──────────────── 2:05 ──────────────── 2:40 ────── 3:00
Context & Corridor     Monthly -> Weekly     CP-SAT Solve &        Live Evaluator         Approval &
Topology Ingestion     Reconciliation        Independent Oracle   Challenge & PlanDiff   Audit Ledger
```

---

### Segment 1: Ground Truth, Topology & Demand Ingestion (0:00 – 0:35)
- **View Target:** `http://localhost:3000/?view=overview` (Corridor Executive Overview)
- **Action:**
  1. Open the Corridor Overview tab. Point to the Vayu-Kosh Corridor (VKC) header badge.
  2. Highlight the fixed spatial topology: 6 stations (Alpha to Foxtrot), dual-track UP/DN lines, and the critical **Traction Neutral Section at Charlie (Km 48.0)**.
  3. Show the sealed snapshot context: 60 monthly departmental demands (Civil P-Way, Electrical TRD, S&T) with explicit safety criticality tiers.
- **Presenter Narration (Verbatim):**
  > *"Judges, welcome to SAMARATH. Railway maintenance cannot rely on black-box probabilistic heuristics. Here you see the Vayu-Kosh Corridor: 120 route-kilometers under 25 kV AC traction. We have ingested 60 multi-departmental demands alongside the active passenger and freight Working Timetable. Notice our provenance tag: everything is strictly grounded in an immutable, cryptographically sealed snapshot."*

---

### Segment 2: Dual-Horizon Monthly-to-Weekly Reconciliation (0:35 – 1:15)
- **View Target:** `http://localhost:3000/?view=maintenance` (Departmental Maintenance Ledger)
- **Action:**
  1. Filter by Department: Civil, Electrical, Signal & Telecom.
  2. Point out the parent-child linkage: 28 operational tasks for Week 40 linked directly to their parent monthly demand envelopes.
  3. Click a task (e.g. `TASK-ELE-0002` at Delta) to open the **Evidence Drawer**.
  4. Show readiness verification: Track machine availability (BCM-01), OHE depot clearance, and crew certifications.
- **Presenter Narration (Verbatim):**
  > *"Every 7-day operational schedule must reconcile against the 30-day monthly plan without unallocated drift. Notice the parent demand keys: Week 40 work orders inherit exact corridor envelopes. The Evidence Drawer proves resource readiness before any solver is invoked — ensuring no uncrewed machine or uncertified gang is ever scheduled."*

---

### Segment 3: Real CP-SAT Optimization & Independent Oracle (1:15 – 2:05)
- **View Target:** `http://localhost:3000/?view=planning` (Operational Planning Workbench)
- **Action:**
  1. Click **"Run Weekly Optimizer"** with the profile set to `PROGRAMME_IMPROVEMENT`.
  2. Observe genuine solver progress transitions in real time:  
     `QUEUED` $\to$ `CLAIMED` $\to$ `BUILDING_CANDIDATES` $\to$ `SOLVING` $\to$ `VERIFYING_FEASIBILITY` $\to$ `COMPLETED`.
  3. Point to the interactive **Time-Distance String Chart**: Show passenger train trajectories with maintenance possession blocks slotted cleanly into freight lull windows and multi-department **Shadow Blocks** (Civil tamping + OHE contact wire inspection co-located under a single traffic power block).
  4. Point to the **Independent Feasibility Checker** badge: "VERIFIED FEASIBLE (0 Conflicts)".
- **Presenter Narration (Verbatim):**
  > *"We now trigger our Google OR-Tools CP-SAT optimizer. Notice the live phase transitions — this is real mathematical solving, not a precomputed mock. Within 2.8 seconds, it generates a mathematically optimal schedule. But crucially, per Indian Railways safety standards, the optimizer cannot grade its own homework. Our autonomous Independent Feasibility Checker verifies track intervals, OHE neutral section isolations, and train headways with zero solver dependencies. Both agree: zero safety violations."*

---

### Segment 4: Live Evaluator Challenge & Dynamic Replanning (2:05 – 2:40)
- **View Target:** `http://localhost:3000/?view=change-review` (Change Review & PlanDiff)
- **Action:**
  1. Invite the evaluator/judge to inject an arbitrary challenge:
     - **Option A:** Machine Breakdown (BCM-01 outage).
     - **Option B:** Emergency Speed Restriction or Window Reduction.
     - **Option C:** Impossible Daytime Window (6-hour block during peak Rajdhani/Shatabdi traffic).
  2. Trigger the event: Watch the **Stable Replanner** (`DISRUPTION_RECOVERY`) execute minimal-churn replanning in $<1.5$ seconds.
  3. Inspect **PlanDiff**: Show visual color coding (Green: Added, Amber: Shifted, Red: Cancelled).
  4. Point to the Stability Index: Unaffected locked blocks are 100% preserved.
  5. For the Impossible Scenario: Point to the **Why-Not Diagnostics** showing the exact Conflict Core (identifying the 6 colliding passenger trains).
- **Presenter Narration (Verbatim):**
  > *"Now, let's put SAMARATH to the test. Evaluator, introduce an unexpected disruption — say, our primary Ballast Cleaning Machine breaks down. Watch the Stable Replanner instantly repair the schedule. Unlike greedy re-solves that scramble the entire corridor, SAMARATH minimizes schedule churn: 26 unaffected commitments remain strictly locked, while the 2 disrupted tasks shift cleanly to Thursday's reserve window. And if an evaluator demands an impossible daytime block over peak express traffic, the system doesn't hallucinate — it returns an evidence-backed Why-Not diagnostic pinpointing the exact conflicting train paths."*

---

### Segment 5: Joint Review, Digital Signature & Handover (2:40 – 3:00)
- **View Target:** `http://localhost:3000/?view=approval` (Joint Review & Audit Ledger)
- **Action:**
  1. Open the Joint Approval Cockpit.
  2. Show multi-department concurrence flags: Senior Divisional Operations Manager (Sr. DOM), Senior Divisional Engineer (Sr. DEN), Senior Divisional Electrical Engineer (Sr. DEE).
  3. Click **"Sign & Seal Programme"**: Generate the immutable SHA-256 cryptographic digital signature.
  4. Show the audit event in the tamper-evident ledger.
- **Presenter Narration (Verbatim):**
  > *"To finalize the weekly block programme, SAMARATH enforces multi-department joint governance. Operating, Engineering, and Electrical officers sign off digitally. The resulting programme is hashed with SHA-256 and sealed in an immutable audit ledger. Any post-approval tampering invalidates the hash. SAMARATH bridges mathematical rigor, railway safety, and field trust."*

---

## 2. Interactive CLI Challenge Guide for Evaluators

For technical evaluators wishing to test the core solver directly via command line:

```powershell
# Run the complete automated challenge suite
python scripts/judge_challenge_harness.py --challenge all

# Test Truthful Unchanged Outcome
python scripts/judge_challenge_harness.py --challenge unchanged

# Test Truthful No-Benefit Timetable Bottleneck
python scripts/judge_challenge_harness.py --challenge no_benefit

# Test Truthful Impossible Mandatory Scenario (returns INFEASIBLE + conflict core)
python scripts/judge_challenge_harness.py --challenge impossible

# Test Machine Outage with Stable Replanner
python scripts/judge_challenge_harness.py --challenge machine_breakdown
```

---

## 3. Video Recording Guidelines (If Required)

- **Resolution:** 1920×1080 (1080p), 60 fps.
- **Audio:** High-fidelity microphone with clear, non-rushed delivery.
- **Footage Policy:** Continuous screen recording. Any time-compressed sequences must display a visible "10× SPEED" watermark. No fabricated latency, savings, or external block grant claims.
