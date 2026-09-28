# Phase 04 Completion Report: Input Gateway, Fictional Corridor Seed, and Provenance

**Phase ID:** PHASE-04  
**Phase Title:** Input Gateway, Fictional Corridor Seed, and Provenance  
**Execution Date:** 2026-09-26  
**Status:** COMPLETED  
**Responsible Agent:** Antigravity Pair Programmer (Solo Build)  

---

## 1. Executive Summary

Phase 04 establishes the end-to-end data ingestion, normalization, and provenance foundations for **SAMARATH**:
1. **Deterministic Vayu-Kosh Corridor (VKC) Seed:**
   - 6 fictional stations spanning 120 km: Alpha (ALP, km 0.0), Bravo (BRV, km 25.0), Charlie (CHR, km 50.0), Delta (DLT, km 75.0), Echo (ECH, km 95.0), Foxtrot (FXT, km 120.0).
   - 10 track segments with dedicated UP/DOWN designations and crossovers.
   - Neutral Section at CHR km 48.0 requiring cross-track OHE de-energization.
   - 60 monthly maintenance demands across Engineering (TMS), Signalling (SMMS), and Electrical (TDMS).
   - 40 weekly train timetable paths spanning passenger, freight, and priority services.
   - 11 machine and gang resource calendars with scheduled maintenance outages.
2. **Formula Injection & Macro Security Invariant:**
   - Microsoft Excel spreadsheets (`.xlsx`) are strictly rejected with HTTP `415 UNSUPPORTED_MEDIA_TYPE` per blueprint architectural decision ADR-011.
   - CSV and JSON inputs are inspected and sanitized; any string values beginning with formula triggers (`=`, `+`, `-`, `@`) are safely escaped with a prepended single-quote to eliminate formula injection.
3. **Quarantine Store & Dry-Run Ingestion:**
   - Validated rows are committed atomically or simulated in dry-run mode.
   - Malformed rows (missing fields, invalid numbers, unparseable dates) are isolated in a thread-safe quarantine store with UUID tracking, line numbers, and exact validation error reasons.
4. **Canonical Snapshots & Fixtures:**
   - Content-addressed snapshots computed via canonical SHA-256 serialization of sorted records.
   - 8 explicit hand-checkable scenario fixtures (`HC-01` to `HC-08`) tagged with `[SYNTHETIC_SCENARIO]` badges and deterministic hashes.
5. **Truthful External Boundary:**
   - Attempted sync with production railway systems (CRIS/COIS) returns HTTP `501 NOT_CONFIGURED` (RFC 7807) rather than simulated mock success.

---

## 2. Verification Evidence and Test Results

### 2.1 Backend Automated Test Suite
All 26 automated tests passed in 1.90s with zero failures:
```
backend/tests/test_auth.py::test_login_success PASSED
backend/tests/test_auth.py::test_login_invalid_password PASSED
backend/tests/test_auth.py::test_admin_cannot_approve_programme PASSED
backend/tests/test_auth.py::test_tms_planner_cannot_alter_tdms PASSED
backend/tests/test_auth.py::test_guest_read_only_access PASSED
backend/tests/test_auth.py::test_corridor_scoped_access PASSED
backend/tests/test_auth.py::test_session_status_and_logout PASSED
backend/tests/test_foundation.py::test_database_connection PASSED
backend/tests/test_foundation.py::test_alembic_applied PASSED
backend/tests/test_foundation.py::test_pydantic_rfc7807_models PASSED
backend/tests/test_foundation.py::test_password_hashing_pbkdf2 PASSED
backend/tests/test_foundation.py::test_health_endpoint PASSED
backend/tests/test_foundation.py::test_readiness_endpoint PASSED
backend/tests/test_foundation.py::test_system_status PASSED
backend/tests/test_foundation.py::test_security_headers PASSED
backend/tests/test_foundation.py::test_cors_preflight PASSED
backend/tests/test_foundation.py::test_api_v1_router_mounted PASSED
backend/tests/test_gateway_ingest.py::test_normalizer_csv_and_json PASSED
backend/tests/test_gateway_ingest.py::test_formula_injection_sanitization PASSED
backend/tests/test_gateway_ingest.py::test_xlsx_unsupported_media_type PASSED
backend/tests/test_gateway_ingest.py::test_duplicate_import_idempotency PASSED
backend/tests/test_gateway_ingest.py::test_dry_run_ingest PASSED
backend/tests/test_gateway_ingest.py::test_quarantine_store_retrieval PASSED
backend/tests/test_gateway_ingest.py::test_canonical_snapshot_sealing PASSED
backend/tests/test_gateway_ingest.py::test_hand_checkable_fixtures PASSED
backend/tests/test_gateway_ingest.py::test_external_sync_501 PASSED

======================== 26 passed in 1.90s ========================
```

### 2.2 Frontend Production Build
TypeScript compilation and Vite production bundling passed with zero errors:
```
> samarath-frontend@0.1.0 build
> tsc && vite build

vite v5.4.21 building for production...
transforming...
✓ 1526 modules transformed.
rendering chunks...
dist/index.html                   0.62 kB │ gzip:  0.38 kB
dist/assets/index-DK6_HlEe.css    1.12 kB │ gzip:  0.61 kB
dist/assets/index-DOkJBDQs.js   237.22 kB │ gzip: 65.02 kB
✓ built in 12.82s
```

---

## 3. Deliverables Produced in Phase 04

1. `backend/app/gateway/normalizer.py`: Normalizer with formula injection sanitization.
2. `backend/app/gateway/quarantine_store.py`: In-memory thread-safe quarantine store.
3. `backend/generate_vkc_seed.py`: Corridor generator creating realistic data files in `backend/app/db/seed_data/`.
4. `backend/app/db/seed_data/`:
   - `corridor_topology.json` (6 stations, 10 track segments, neutral section).
   - `demands_monthly_60.json` (60 monthly maintenance demands).
   - `train_timetable.json` (40 weekly train paths).
   - `resource_calendars.json` (11 machine and gang calendars).
   - `hand_checkable_fixtures.json` (8 explicit hand-checkable scenario fixtures).
5. `backend/app/gateway/service.py`: Seeding, ingestion, snapshot sealing, and fixtures.
6. `backend/app/api/v1/gateway.py`: REST gateway endpoints (`/seed/corridor`, `/import`, `/quarantine`, `/snapshots/seal`, `/snapshots`, `/fixtures`, `/external/sync`).
7. `backend/app/api/v1/tasks.py`: Task queries, filtering, and revision updates.
8. `backend/tests/test_gateway_ingest.py`: 9 automated gateway tests.
9. `frontend/src/views/MaintenanceView.tsx`: Real backend data queries with live counters and seeding trigger.
10. `frontend/src/views/DataView.tsx`: 5-tab interface for manifests, ingest, quarantine, snapshots, and fixtures.

---

## 4. Exit Gate Assessment & Readiness

- [x] CSV and JSON adapters produce normalized, validated domain models.
- [x] XLSX rejected with `415 UNSUPPORTED_MEDIA_TYPE` to prevent formula/macro security vulnerabilities.
- [x] Formula injection attacks (`=`, `+`, `-`, `@`) automatically neutralized.
- [x] Fictional VKC corridor seeded with 6 stations, 10 segments, 60 demands, 40 train paths, and 11 resources.
- [x] 8 hand-checkable test fixtures with deterministic hashes and `[SYNTHETIC_SCENARIO]` badges.
- [x] Canonical snapshot hashing via SHA-256 for deterministic reproducibility.
- [x] External CRIS/COIS sync returns explicit `501 NOT_CONFIGURED`.
- [x] 26 backend tests passing; frontend builds cleanly.

**Verdict:** **EXIT GATE G1-04 PASSED.**  
**Next Runnable Phase:** **Phase 05: Readiness, Compatibility, and Executable Work Packages.**
