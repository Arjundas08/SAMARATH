# Phase 00 Completion Report: Repository Audit and Implementation Contract

**Phase ID:** PHASE-00  
**Phase Title:** Repository Audit and Implementation Contract  
**Execution Date:** 2026-09-26  
**Status:** COMPLETED  
**Responsible Agent:** Antigravity Pair Programmer (Solo Build)  

---

## 1. Executive Summary

Phase 00 establishes the frozen engineering baseline, source-of-truth typed contracts, architectural decision records, and acceptance matrices for **SAMARATH** (System for Automated Maintenance Allocation, Rolling Availability, and Track Harmony) under Smart India Hackathon 2026 Problem Statement **SIH26027**.

This phase does not claim to deliver a working end-to-end prototype; instead, it establishes the rigorous project control foundation required to build a production-grade railway optimization system that withstands live evaluator disruption challenges.

---

## 2. Codebase Audit Findings and Component Decisions

A granular inspection of the existing workspace (`samarth_system`) was conducted to evaluate existing code, tests, and dependencies.

### 2.1 Preserved and Adapted Assets
1. **Mathematical Optimization Logic:**
   - The OR-Tools CP-SAT formulation logic in `backend/app/engine/cp_sat_solver.py` provides foundational patterns for variable creation and linear constraint indexing.
   - Preserved and adapted into `backend/app/engine/optimizer.py` under the frozen lexicographic profiles.
2. **Domain Field Definitions:**
   - Field definitions from `backend/app/domain/` for assets, maintenance types, and trains provided reference for the normalized schemas in `docs/API_CONTRACT.md`.
3. **Safety Buffer Rules:**
   - The headway and clearance calculation heuristics in `backend/app/rules/safety_validator.py` are preserved and refactored into the autonomous `app.checker.feasibility_checker` module.
4. **Presentation Collateral:**
   - Static landing page scripts (`build_landing_page.py`) are archived in `frontend/legacy_landing/` for reference and demonstration deck materials.

### 2.2 Replaced and Re-architected Components
1. **Database Architecture:**
   - *Previous:* SQLite (`samarth.db`) without migration history or foreign key cascade semantics.
   - *New:* PostgreSQL 16 with full Alembic migration versioning, strict foreign keys, and relational integrity.
2. **Verification Independence:**
   - *Previous:* Validator was deeply intertwined with solver domain models.
   - *New:* Autonomous Feasibility Checker reading raw snapshots without solver coupling, enforcing the Oracle pattern.
3. **Protected Commitments:**
   - *Previous:* Planned assignments treated commitments as soft objective penalties.
   - *New:* Per user correction and ADR-006, hard locks and protected commitments are unyielding physical constraints.
4. **Execution Paradigm:**
   - *Previous:* Synchronous HTTP execution causing worker blocking.
   - *New:* PostgreSQL leased outbox worker queue supporting asynchronous solves and resilient crash recovery.
5. **Frontend Application:**
   - *Previous:* Single static HTML landing page.
   - *New:* React 18 + TypeScript operational planning workbench with ECharts time-distance string charts following the "Signal & Slate" design brief.

---

## 3. Verified Compatible Dependency Matrix

Rather than unverified "latest stable" dependencies, all core packages are pinned to mutually verified, compatible versions:

### 3.1 Backend Dependencies (`backend/pyproject.toml`)
- `python = ">=3.11,<3.13"`
- `fastapi == 0.111.0` (High-performance async ASGI web framework)
- `uvicorn[standard] == 0.30.1` (Production ASGI server)
- `pydantic == 2.8.2` (Type validation and serialization)
- `pydantic-settings == 2.3.4` (Environment configuration)
- `ortools == 9.10.4067` (Google OR-Tools with CP-SAT constraint solver)
- `sqlalchemy == 2.0.31` (Modern Python SQL toolkit and ORM)
- `alembic == 1.13.2` (Database schema migrations)
- `asyncpg == 0.29.0` (Async PostgreSQL driver)
- `psycopg2-binary == 2.9.9` (Sync PostgreSQL driver for Alembic migrations)
- `python-jose[cryptography] == 3.3.0` (JWT signature verification)
- `passlib[bcrypt] == 1.7.4` (Secure credential hashing)
- `pytest == 8.2.2` (Test framework)
- `pytest-asyncio == 0.23.8` (Async test runner)
- `httpx == 0.27.0` (HTTP client for API testing)

### 3.2 Frontend Dependencies (`frontend/package.json`)
- `react == ^18.3.1`
- `react-dom == ^18.3.1`
- `typescript == ^5.5.3`
- `vite == ^5.3.4`
- `echarts == ^5.5.1` (Apache ECharts for time-distance string charts)
- `lucide-react == ^0.400.0` (Accessible SVG iconography)
- `@types/react == ^18.3.3`
- `@types/react-dom == ^18.3.0`
- `@types/node == ^20.14.10`

---

## 4. Canonical Project Commands

All development, testing, and deployment operations follow standardized commands:

### 4.1 Environment Setup & Database
```powershell
# Start local PostgreSQL container
docker compose -f deploy/docker-compose.yml up -d db

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Seed demonstration corridor data (VKC)
python -m app.db.seed
```

### 4.2 Running Services
```powershell
# Run API server (FastAPI)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Run background solve worker
python -m app.workers.solve_worker

# Run frontend development server
cd ../frontend
npm install
npm run dev
```

### 4.3 Testing & Quality Assurance
```powershell
# Run backend test suite
cd backend
pytest -v

# Run type checking
mypy app

# Run frontend test & build
cd ../frontend
npm run build
```

---

## 5. Deliverables Produced in Phase 00

1. `docs/DECISIONS.md`: 12 Architecture Decision Records (ADR-001 through ADR-012).
2. `docs/SCOPE.md`: Complete specification of the Vayu-Kosh Corridor (VKC), station topology, track sections, and workload boundaries.
3. `docs/API_CONTRACT.md`: Strict JSON schemas and RFC 7807 error formats for all core domain entities.
4. `docs/ACCEPTANCE_MATRIX.md`: End-to-end traceability mapping SIH requirements to automated tests and exit gates.
5. `docs/IMPLEMENTATION_STATE.md`: Active project tracker recording true verified capability status.
6. `docs/phase-reports/PHASE-00.md`: This completion report.

---

## 6. Exit Gate Assessment & Readiness

- [x] All 20 phases mapped to requirement IDs, owner skills, prerequisites, and exit gates.
- [x] Source-of-truth schemas defined for Task, Snapshot, CandidateManifest, Assignment, SolverRun, ValidationResult, PlanVersion, Reason, PlanDiff, and PlanMetric.
- [x] Hard locks and protected commitments formally established as hard mathematical constraints.
- [x] Two distinct objective profiles defined (`PROGRAMME_IMPROVEMENT` and `DISRUPTION_RECOVERY`).
- [x] Dependencies pinned to verified compatible versions.
- [x] Monorepo layout and canonical commands established.

**Verdict:** **EXIT GATE G0-00 PASSED.**  
**Next Runnable Phase:** **Phase 01: Runnable Foundation, Database, and Typed Contracts.**
