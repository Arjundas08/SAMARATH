# System Scope and Demonstration Corridor Specification - SAMARATH

**Project:** SAMARATH  
**Problem Statement:** SIH26027 (Ministry of Railways, Smart India Hackathon 2026)  
**Status:** FROZEN BASELINE (Phase 00)  
**Last Updated:** 2026-09-26  

---

## 1. System Mission and Boundaries

SAMARATH is a territory-scoped decision-support platform designed to automate and optimize Rolling Block Planning for Indian Railways. It ingests versioned maintenance demands, timetable paths, and resource calendars, synthesizing them into conflict-free monthly block allocations and weekly execution schedules.

### Explicit System Boundaries

| Functional Domain | In Scope (SAMARATH Responsibility) | Out of Scope (External Railway Responsibility) |
|---|---|---|
| **Demand Capture** | Ingest, parse, and validate departmental maintenance demands (TMS, SMMS, TDMS) with schema integrity checks. | Creation of raw engineering defect reports or asset maintenance regimes. |
| **Timetable Integration** | Ingest working timetables (WTT) and freight forecasts; model spatio-temporal track occupation. | Dispatching active trains, running Section Control, or issuing train orders. |
| **Multi-Department Coordination** | Identify geographic/temporal overlap to bundle civil, OHE, and signal blocks into single possessions. | Direct supervisory management of field maintenance gangs and contractors. |
| **Optimization** | Formulate and solve multi-objective CP-SAT models generating optimal start/end times and tracks. | Manual overrides without validation; unconstrained arbitrary scheduling. |
| **Safety & Feasibility Verification** | Deterministic, independent rule verification (track conflict, power block isolation, resource clash). | Physical inspection of track conditions or testing of interlocking hardware. |
| **Operational Block Grant** | Propose approved programmes with audit trails and signature manifests. | **Granting, extending, or releasing actual physical line blocks or Power Blocks (PTW).** |

> [!IMPORTANT]
> **Operational Block Authority Invariant:** SAMARATH proposes programmes; it never grants, activates, or releases live operational blocks. Field block granting remains the exclusive statutory responsibility of the Section Controller and Station Master under Indian Railways General & Subsidiary Rules (G&SR).

---

## 2. Bounded Demonstration Corridor: "Vayu-Kosh Corridor" (VKC)

To enable exhaustive verification, deterministic scenario injection, and rapid evaluator challenge during hackathon judging, the baseline system operates on a verified, bounded corridor model.

### 2.1 Corridor Topology

The **Vayu-Kosh Corridor (VKC)** is a 120.0-kilometer electrified double-track main line section connecting 6 fictional stations.

```
[STN-01: Alpha] ====== [STN-02: Bravo] ====== [STN-03: Charlie] ====== [STN-04: Delta] ====== [STN-05: Echo] ====== [STN-06: Foxtrot]
Km 0.000               Km 22.500              Km 48.000               Km 73.200              Km 96.800              Km 120.000
    |                      |                      |                       |                      |                      |
[Crossover]            [Crossover]            [Crossover]             [Crossover]            [Crossover]            [Crossover]
```

### 2.2 Station Specifications

| Station Code | Station Name | Chainage (Km) | Absolute Distance (m) | Track Lines | Crossover Facility | Signaling System |
|---|---|---|---|---|---|---|
| **ALP** | Alpha | 0.000 | 0 | 4 (UP Main, DN Main, Loop 1, Loop 2) | Yes (Universal) | Electronic Interlocking (EI) |
| **BRV** | Bravo | 22.500 | 22,500 | 3 (UP Main, DN Main, Common Loop) | Yes (Facing/Trailing) | Electronic Interlocking (EI) |
| **CHR** | Charlie | 48.000 | 48,000 | 4 (UP Main, DN Main, Loop 1, Loop 2) | Yes (Universal) | Electronic Interlocking (EI) |
| **DLT** | Delta | 73.200 | 73,200 | 3 (UP Main, DN Main, Common Loop) | Yes (Facing/Trailing) | Electronic Interlocking (EI) |
| **ECH** | Echo | 96.800 | 96,800 | 2 (UP Main, DN Main) | No (Block Station) | Absolute Block / EI |
| **FXT** | Foxtrot | 120.000 | 120,000 | 4 (UP Main, DN Main, Loop 1, Loop 2) | Yes (Universal) | Electronic Interlocking (EI) |

### 2.3 Track and Block Sections

1. **Lines:**
   - **UP Line:** Direction Foxtrot $\rightarrow$ Alpha (Decreasing chainage: 120 km down to 0 km).
   - **DN Line:** Direction Alpha $\rightarrow$ Foxtrot (Increasing chainage: 0 km up to 120 km).
2. **Block Sections:** 5 inter-station block sections per line (10 directional block sections total):
   - `SEC-01`: Alpha $\leftrightarrow$ Bravo (22.5 km)
   - `SEC-02`: Bravo $\leftrightarrow$ Charlie (25.5 km)
   - `SEC-03`: Charlie $\leftrightarrow$ Delta (25.2 km)
   - `SEC-04`: Delta $\leftrightarrow$ Echo (23.6 km)
   - `SEC-05`: Echo $\leftrightarrow$ Foxtrot (23.2 km)
3. **Automatic Signalling & Headway:**
   - Standard minimum headway buffer between consecutive trains: **10 minutes**.
   - Minimum safety buffer between train passage and block occupation: **15 minutes**.
   - Maximum permissible speed (MPS): **130 km/h** (Passenger/Express), **75 km/h** (Freight).

### 2.4 Traction Distribution (TRD / OHE) Sub-Sectors

The corridor is energized with 25 kV AC single-phase traction with 3 Traction Substations (TSS) and intermediate Sectioning and Paralleling Posts (SP / SSP):
- **TSS-1 (Alpha):** Feeds Section Alpha to Charlie (Km 0.0 to 48.0).
- **SP-1 (Charlie):** Neutral Section at Km 48.0 (Phase break).
- **TSS-2 (Delta):** Feeds Section Charlie to Delta (Km 48.0 to 73.2).
- **SSP-2 (Echo):** Sectioning post at Km 96.8.
- **TSS-3 (Foxtrot):** Feeds Section Delta to Foxtrot (Km 73.2 to 120.0).

> [!NOTE]
> **Electrical Isolation Rule:** Any maintenance demand requiring an OHE Power Block de-energizes the corresponding elementary section. If a civil track machine exceeds standard clearance (e.g., BCM, TRT), a mandatory concurrent OHE Permit-to-Work (PTW) is automatically enforced.

---

## 3. Departmental Demand Profiles

SAMARATH integrates maintenance demands from the three principal railway engineering departments:

### 3.1 Engineering (Civil / Permanent Way - TMS)
- **Asset Classes:** Rail, Sleepers, Ballast, Turnouts, Formations.
- **Key Machines:**
  - `BCM` (Ballast Cleaning Machine): Requires 4-hour block, 30 min setup, 30 min restoration. Minimum contiguous window 240 mins.
  - `CSM` / `Tamping` (Continuous Tamping Machine): Requires 2.5-hour block.
  - `DGS` (Dynamic Track Stabilizer): Follows tamping in integrated tandem pack.
  - `TRT` (Track Relaying Train): Requires 4 to 6-hour block.
- **Criticality Tiers:** Statutory Safety (Tier 1 - Mandatory), Speed Restriction Relief (Tier 2), Routine Cyclic (Tier 3).

### 3.2 Electrical (Traction Distribution - TDMS)
- **Asset Classes:** Contact wire, Catenary wire, Insulators, Cantilevers, Neutral sections.
- **Key Machines:**
  - `Tower Wagon` (OHE Inspection / Maintenance Car): Requires 2 to 3-hour power block.
  - `Wiring Train`: Heavy OHE rehabilitation, requires 4-hour power and traffic block.
- **Safety Precondition:** Must be de-energized and earthed before work commencement.

### 3.3 Signalling & Telecommunication (S&T - SMMS)
- **Asset Classes:** Point machines, Track circuits, Axle counters, Signal aspects, Electronic Interlocking units.
- **Characteristics:** Frequently executed as "shadow blocks" during civil or OHE blocks in station limits.
- **Disconnection Notice:** Mandatory formal disconnection/reconnection workflow.

---

## 4. Benchmark Workload Sizing

For system testing, demonstration, and evaluation benchmarking:
1. **Monthly Planning Horizon:**
   - 30 consecutive calendar days.
   - Total maintenance demands: **60 tasks** across all 3 departments.
   - Train traffic density: ~40 trains per 24-hour cycle (24 Passenger/Express + 16 Freight).
2. **Weekly Detailed Horizon:**
   - 7 consecutive calendar days (Monday 00:00 to Sunday 23:59 IST).
   - Selected/reconciled work packages: **Up to 30 tasks**.
   - Minute-exact resolution for machine positioning, train headway margins, and power isolation.
3. **Solver Performance Target:**
   - Candidate Generation: $< 1.5$ seconds for 30 tasks.
   - CP-SAT Optimization: $< 15$ seconds for optimal/near-optimal solution.
   - Independent Checker Validation: $< 0.5$ seconds across 100% of candidate assignments.
