# Architecture Decision Records (ADRs) - SAMARATH

**Project:** SAMARATH (System for Automated Maintenance Allocation, Rolling Availability, and Track Harmony)  
**Problem Statement:** SIH26027 (Ministry of Railways, Smart India Hackathon 2026)  
**Document Status:** FROZEN BASELINE (Phase 00)  
**Last Updated:** 2026-09-26  

---

## ADR-001: Monorepo Layout and Unified Technology Stack

### Context
SAMARATH requires high-performance mathematical optimization, strict transactional audit logging, an independent correctness oracle, and a real-time reactive operational workbench.

### Decision
1. **Repository Layout:** Monorepo containing:
   - `backend/`: Python 3.11+ modular package (`app/`) containing API, domain models, CP-SAT solver, independent checker, durable worker, and migration scripts.
   - `frontend/`: React 18+ with TypeScript, Vite, Vanilla CSS/CSS variables design system, and Apache ECharts.
   - `docs/`: System documentation, prompt pack, phase reports, and ADRs.
   - `deploy/`: Docker Compose configuration for PostgreSQL and services.
2. **Backend Engine:** Python with FastAPI for HTTP/REST contracts, Pydantic v2 for typed validation, SQLAlchemy 2.0 + Alembic for PostgreSQL persistence, and Google OR-Tools CP-SAT as the core constraint optimization engine.
3. **Frontend Stack:** React 18 with TypeScript, Vite for build tooling, Apache ECharts for time-distance string charts and resource histograms, and native CSS design tokens based on the "Signal & Slate" design brief.
4. **Exclusions:** No Redis, No Celery, No Kafka, No external proprietary LLM runtime in the critical planning path, and no unvalidated microservices.

### Consequences
- Single development environment, zero multi-repo coordination overhead.
- Direct TypeScript type generation from Pydantic schemas ensures compile-time frontend-backend contract guarantees.

---

## ADR-002: Bounded Fictional Demonstration Corridor

### Context
Indian Railways comprises thousands of stations and vast interconnected networks. An unconstrained deployment would obscure algorithmic verification with missing national topology data.

### Decision
Freeze a bounded, representative demonstration corridor:
1. **6 Fictional Stations:** Alpha (Km 0.0), Bravo (Km 22.5), Charlie (Km 48.0), Delta (Km 73.2), Echo (Km 96.8), Foxtrot (Km 120.0).
2. **Track Layout:** Double-track line with bidirectional signalling capabilities (UP line: Foxtrot -> Alpha; DOWN line: Alpha -> Foxtrot), with crossover points at stations Bravo, Charlie, and Delta.
3. **Electrification:** 25 kV AC overhead catenary (OHE) with neutral sections and designated electrical sub-sectors (TRD).
4. **Departments:** 
   - Civil/Permanent Way (Track - TMS)
   - Signalling & Telecommunication (S&T - SMMS)
   - Electrical/Traction Distribution (TRD - TDMS)
5. **Workload Sizing:** 60 maintenance demands across a 30-day calendar month; up to 30 fine-grained work packages scheduled in any active 7-day weekly horizon.

### Consequences
- Sizing allows exhaustive verification, deterministic scenario injection, and instant visual validation during judge review without timeouts.

---

## ADR-003: Time Units, Coordinate System, and Localization

### Context
Railway operations span time zones, shifts, and rolling 24-hour cycles. Ambiguity in time zones or continuous floating-point timestamps introduces solver numerical instability and display discrepancies.

### Decision
1. **Storage Format:** All timestamps in the database and JSON wire payloads are stored as UTC ISO 8601 strings (e.g., `2026-10-12T02:00:00Z`).
2. **Internal Optimization Units:** The CP-SAT solver and Independent Checker operate strictly on integer minutes relative to a fixed horizon epoch $T_0$ (e.g., minute 0 = Monday 00:00:00 UTC).
3. **Display Representation:** All user interfaces, charts, and audit views project timestamps in **Indian Standard Time (IST / Asia/Kolkata, UTC+05:30)**.
4. **Spatial Coordinates:** Linear chainage stored as integer meters from corridor origin (0 to 120,000 meters). Station locations and track segments are discrete topological blocks with continuous metric boundaries.

### Consequences
- Eliminates daylight saving edge cases, floating point rounding errors in constraint formulation, and time zone presentation drift.

---

## ADR-004: Three Strict Data Provenance Modes

### Context
Presenting synthetic or simulated test data as live Indian Railways operational data violates competition integrity. Conversely, rejecting synthetic test scenarios prevents rigorous stress-testing.

### Decision
Every dataset, task, timetable, and solver run is explicitly tagged with one of three immutable provenance modes:
1. `TEST`: Synthetic, bounded demonstration corridor data designed for functional unit, integration, and UI testing. Always prominently labelled with a persistent visual badge (`[TEST]`).
2. `SYNTHETIC_SCENARIO`: Deterministically perturbed scenarios (e.g., delayed trains, machine breakdown, emergency work) used for evaluator challenge and disruption recovery demonstration.
3. `AUTHORIZED_IMPORT`: Records imported via approved administrative batch upload conforming strictly to the official schema.

### Consequences
- Complete transparency: no judge or operator can mistake a demo or synthetic stress run for live railway operational feeds.

---

## ADR-005: Separation of Demand, Programme, and Field Authority

### Context
A planning tool must never conflate requesting work, proposing a coordinated schedule, and granting permission to enter a live railway track.

### Decision
Enforce three distinct, non-overlapping operational lifecycles:
1. **Demand State (Departmental Need):** Managed by TMS, SMMS, TDMS. States: `DRAFT` -> `SUBMITTED` -> `VALIDATED` -> `SUPERSEDED` / `WITHDRAWN`.
2. **Programme State (SAMARATH Proposed Plan):** Generated by CP-SAT solver and validated by the Independent Checker. States: `DRAFT_PROPOSAL` -> `CHECKED_FEASIBLE` -> `JOINT_REVIEW` -> `APPROVED_PROGRAMME` -> `STALE` / `REVISED`.
3. **Operational Railway Authority (Field Execution):** Strictly external. SAMARATH proposes programmes; **it never grants, extends, or releases an operational block**. The software displays external authority observations as read-only status (`NOT_REQUESTED`, `EXTERNAL_PERMIT_GRANTED`, `WORK_IN_PROGRESS`, `CLEARED`).

### Consequences
- Architectural adherence to Indian Railways General & Subsidiary Rules (G&SR) and Railway Board Joint Rolling Block Planning Guidelines (Aug 2023).

---

## ADR-006: Protected Commitments and Hard Locks as Constraints

### Context
In earlier drafts, commitments were described as an objective tier. The user clarified and corrected: hard locks must be physical constraints; only negotiable preferences belong in optimization objectives.

### Decision
1. **Hard Locks as Constraints:** Any task or assignment marked `LOCKED` (e.g., approved contractor possession, emergency speed restriction repair, passenger train guarantee) is instantiated as an unyielding hard equality constraint in the CP-SAT model:
   $$\text{start}(i) = t_{\text{locked}}, \quad \text{assigned}(i) = 1$$
2. **Rejection of Soft Locks:** Protected commitments are never relaxed or violated to improve a global objective score. If a new disturbance makes a hard lock physically impossible, the solver returns `INFEASIBLE` with an explicit conflict core rather than silently displacing the locked block.
3. **Negotiable Preferences:** Only non-locked tasks, flexible start intervals, and secondary resource allocations are subject to objective optimization trade-offs.

### Consequences
- Operational trust: planners know that a committed block will never be shifted behind their backs by an algorithm.

---

## ADR-007: Two Distinct Lexicographic Objective Profiles

### Context
Routine monthly planning seeks asset availability and efficiency, whereas mid-week disruption recovery must minimize schedule disruption and preserve existing plans.

### Decision
Formulate two strictly separate, frozen lexicographic objective profiles:

#### Profile 1: `PROGRAMME_IMPROVEMENT` (Routine Planning)
1. **Tier 1 (Feasibility & Mandatory Work):** Maximize completion of statutory safety and mandatory overdue work ($W_{\text{mandatory}} \gg W_{\text{routine}}$).
2. **Tier 2 (Priority & Deadlines):** Minimize weighted tardiness against target maintenance deadlines across TMS, SMMS, and TDMS.
3. **Tier 3 (Train Availability & Operating Impact):** Minimize total corridor occupation penalty and train headway buffer infringement proxy.
4. **Tier 4 (Multi-Department Bundling):** Maximize shadow-block coordination (bundling civil, OHE, and signalling works in identical spatio-temporal envelopes).
5. **Tier 5 (Mobilization Stability):** Minimize machine deadheading and crew dead time.

#### Profile 2: `DISRUPTION_RECOVERY` (Event-Driven Replanning)
1. **Tier 1 (Hard Invariants & Locked Commitments):** Zero tolerance for violation of preserved commitments and physical block safety.
2. **Tier 2 (Critical Coverage Protection):** Guarantee critical infrastructure inspection coverage before any optimization of routine tasks.
3. **Tier 3 (Minimal Schedule Churn / Stability):** Minimize the cardinality and time-displacement of changes relative to the incumbent approved plan:
   $$\min \sum_{i} \left( |\Delta \text{start}_i| + \lambda \cdot [i \text{ rescheduled or cancelled}] \right)$$
4. **Tier 4 (Marginal Efficiency):** Optimize secondary efficiency metrics only within the bounded neighborhood of surviving tasks.

### Consequences
- Deterministic behavior: prevents the solver from radically overturning a weekly schedule during a minor delay.

---

## ADR-008: Independent Deterministic Feasibility Checker (Oracle)

### Context
Optimizers can contain formulation bugs, solver precision bugs, or invalid relaxations. An optimization model must never certify its own validity.

### Decision
1. Implement a completely independent verification module: `app.checker.feasibility_checker`.
2. The Checker accepts only:
   - The raw, immutable `Snapshot` (topology, train paths, demands, safety rules).
   - The candidate assignment manifest (task, track, start time, end time, resources).
3. The Checker executes zero CP-SAT or OR-Tools code. It evaluates purely deterministic, physical rules:
   - Track spatial conflict (no two trains or blocks occupying the same block section simultaneously).
   - Electrical isolation safety (OHE power block overlaps with work package).
   - Machine and crew capability and clash checking.
   - Setup and restoration headway buffers.
4. If the Checker detects any conflict or if evidence for a rule is missing, it returns `VERIFICATION_FAILED` or `UNKNOWN` (treated as blocking). A plan cannot be marked feasible or approved without the Checker's digital stamp.

### Consequences
- High-integrity architecture matching the 20-diagram specification (D02 & D07).

---

## ADR-009: Durable Leased Background Jobs via PostgreSQL Outbox

### Context
Solving 60 monthly tasks or 30 weekly tasks takes between 2 and 60 seconds. Running optimization synchronously in HTTP request threads causes client timeouts, while Redis/Celery introduces unneeded operational dependencies.

### Decision
1. Implement durable background execution directly in PostgreSQL:
   - Table `solver_jobs`: contains `job_id`, `snapshot_id`, `profile`, `status` (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`, `CANCELLED`), `lease_owner`, `lease_expires_at`, `result_summary`, and `error_detail`.
2. A lightweight background worker process polls for available jobs, acquires atomic leases using `SELECT ... FOR UPDATE SKIP LOCKED`, and executes the solve job.
3. The frontend polls job status via `/api/v1/jobs/{job_id}` and receives final materialized results.

### Consequences
- Zero external message brokers required for hackathon deployment; fully crash-resilient; complete job history persisted in relational storage.

---

## ADR-010: Pinned Dependencies and Reproducible Environment Strategy

### Context
Relying on floating or "latest stable" dependencies creates non-reproducible builds, unexpected API breaks, and silent solver behavior shifts.

### Decision
Explicitly pin all core dependencies to verified compatible versions:
- Python 3.11+:
  - `fastapi==0.111.0`
  - `uvicorn[standard]==0.30.1`
  - `pydantic==2.8.2`
  - `pydantic-settings==2.3.4`
  - `ortools==9.10.4067`
  - `sqlalchemy==2.0.31`
  - `alembic==1.13.2`
  - `asyncpg==0.29.0`
  - `psycopg2-binary==2.9.9`
  - `pytest==8.2.2`
  - `httpx==0.27.0`
  - `python-jose[cryptography]==3.3.0`
  - `passlib[bcrypt]==1.7.4`
- Frontend:
  - `react@^18.3.1`
  - `react-dom@^18.3.1`
  - `typescript@^5.5.3`
  - `vite@^5.3.4`
  - `echarts@^5.5.1`
  - `lucide-react@^0.400.0`

### Consequences
- 100% reproducible development and evaluation environments.

---

## ADR-011: Simulator and Synthetic Scenario Policy

### Context
Simulation can either be a powerful verification tool or deceptive if presented as live data.

### Decision
1. Deterministic scenario simulation and synthetic disruption generators (e.g., train delay injector, equipment breakdown simulator) are retained and supported.
2. Synthetic scenarios are strictly labelled as `SYNTHETIC_SCENARIO` and routed through the exact same snapshot, optimizer, and independent checker pipeline as standard inputs.
3. Under no circumstances will mock or hard-coded schedules be returned as solver outputs.

### Consequences
- Full compliance with SIH evaluation rules and engineering integrity.

---

## ADR-012: Frontend Architecture and Legacy Preservation

### Context
The previous repository contained landing page generation scripts.

### Decision
1. Build the primary operational workbench in `frontend/` as a React 18 + TypeScript SPA implementing the seven functional destinations from the Design Brief.
2. Preserve existing landing page artifacts in `frontend/legacy_landing/` for reference and presentation materials without coupling them to the operational planning route hierarchy.

### Consequences
- Focuses operational review on the planning cockpit while preserving previous collateral.
