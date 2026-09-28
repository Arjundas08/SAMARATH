# Phase 02 Completion Report: Real Login, Scoped Permissions, and Secure Sessions

**Phase ID:** PHASE-02  
**Phase Title:** Real Login, Scoped Permissions, and Secure Sessions  
**Execution Date:** 2026-09-26  
**Status:** COMPLETED  
**Responsible Agent:** Antigravity Pair Programmer (Solo Build)  

---

## 1. Executive Summary

Phase 02 delivers a production-grade, secure authentication and Role-Based Access Control (RBAC) foundation for **SAMARATH**:
1. **Backend-for-Frontend (BFF) Session Security:**
   - Session authentication implemented via `HttpOnly`, `SameSite=Lax` cookies (`samarath_session`).
   - Pure JWT tokens are never exposed to browser `localStorage` or JavaScript execution context.
   - CSRF protection enabled via separate `samarath_csrf` cookie and header verification.
2. **Standard Cryptography & Hashing:**
   - Standard library PBKDF2-HMAC-SHA256 password hashing with 100,000 iterations and 16-byte cryptographically secure random salt, ensuring zero C-extension incompatibilities.
   - JWT token issuance with strict `iss` (`samarath-auth-service`), `aud` (`samarath-api`), algorithm (`HS256`), and expiration checking.
3. **9 Fictional Functional Roles with Multi-Dimension Scoping:**
   - Departmental Planners (`planner_tms`, `planner_smms`, `planner_tdms`) scoped by department (`ENGINEERING`, `SIGNALLING`, `ELECTRICAL`) and territory (`VKC`).
   - Corridor Coordinator (`coordinator_vkc`) for multi-department coordination.
   - Operating Reviewer (`reviewer_operating`) for timetable inspection and conflict resolution.
   - Delegated Programme Approver (`approver_operating`) with statutory authority to approve rolling programmes (`PROGRAMME_APPROVE`).
   - Integration Operator (`operator_ingest`) for data ingestion and snapshot sealing.
   - Rule Author and Approver (`author_rules`, `approver_rules`).
   - Safety Auditor (`auditor_safety`) for read-only ledger audit access.
   - Infrastructure Administrator (`admin_infra`) for database and systems operations.
4. **Architectural Invariant Verification (Diagram D16):**
   - **Administrator Separation:** The Infrastructure Administrator has system admin rights, but is strictly prohibited from approving operational maintenance programmes.
   - **Departmental Isolation:** Track planners cannot modify OHE or Signalling demands; cross-department mutations are rejected with 403 Forbidden.
   - **Client Trust Invariant:** Never trust role, department, or territory sent from the client; all authorization context is derived exclusively from the verified server-signed session.

---

## 2. Verification Evidence and Test Results

### 2.1 Backend Automated Test Suite
All 17 automated tests passed (`pytest tests/ -v`):
```
tests/test_auth_rbac.py::test_login_success_and_cookie_issuance PASSED   [  5%]
tests/test_auth_rbac.py::test_login_invalid_credentials_rejected PASSED  [ 11%]
tests/test_auth_rbac.py::test_logout_clears_cookies PASSED               [ 17%]
tests/test_auth_rbac.py::test_unauthenticated_request_returns_401 PASSED [ 23%]
tests/test_auth_rbac.py::test_session_inspection_reflects_authenticated_identity PASSED [ 29%]
tests/test_auth_rbac.py::test_delegated_approver_can_approve_programme PASSED [ 35%]
tests/test_auth_rbac.py::test_planner_cannot_approve_programme PASSED    [ 41%]
tests/test_auth_rbac.py::test_administrator_cannot_approve_programme PASSED [ 47%]
tests/test_auth_rbac.py::test_departmental_isolation_enforced PASSED     [ 52%]
tests/test_contracts.py::test_task_valid_creation PASSED                 [ 58%]
tests/test_contracts.py::test_task_invalid_chainage_rejection PASSED     [ 64%]
tests/test_contracts.py::test_task_power_block_missing_section PASSED    [ 70%]
tests/test_contracts.py::test_rfc7807_validation_error_response PASSED   [ 76%]
tests/test_database_smoke.py::test_schema_creation_and_relational_integrity PASSED [ 82%]
tests/test_health.py::test_health_endpoint PASSED                        [ 88%]
tests/test_snapshot_hashing.py::test_snapshot_hashing_determinism_under_permutation PASSED [ 94%]
tests/test_snapshot_hashing.py::test_snapshot_hashing_changes_on_content_revision PASSED [100%]

======================= 17 passed in 5.37s =======================
```

### 2.2 Frontend Build and Interactive Shell Verification
- Full TypeScript compilation and Vite bundling passed (`npm run build` in 6.51s).
- Live identity pill in top navigation bar shows authenticated user, display name, and quick logout affordance.
- Interactive authentication dialog allows evaluator to switch between realistic bootstrap roles (`reviewer_operating`, `approver_operating`, `planner_tms`, etc.).

---

## 3. Deliverables Produced in Phase 02

1. `backend/app/core/security.py`: Standard library PBKDF2-HMAC-SHA256 password hashing, JWT creation/decoding, and CSRF token verification.
2. `backend/app/core/auth.py`: In-memory bootstrap users, authentication dependencies, permission checks, department isolation, and territory guards.
3. `backend/app/schemas/auth.py`: Pydantic schemas for `UserRole`, `Permission`, `LoginRequest`, and `SessionResponse`.
4. `backend/app/api/v1/auth.py`: Endpoints for `POST /api/v1/auth/login`, `POST /api/v1/auth/logout`, and `GET /api/v1/auth/session`.
5. `backend/app/api/v1/rbac_demo.py`: Protected endpoints verifying operational programme approval authority and departmental demand isolation.
6. `backend/tests/test_auth_rbac.py`: 9 granular automated tests covering authentication and RBAC invariants.
7. `frontend/src/types/api.ts`: Updated TypeScript types including all auth schemas and roles.
8. `frontend/src/components/AppShell.tsx`: Interactive identity indicator and role switcher modal.

---

## 4. Exit Gate Assessment & Readiness

- [x] HttpOnly, SameSite session cookie authentication implemented; no tokens in localStorage.
- [x] Multi-dimension scoping (role, department, territory) strictly enforced on backend.
- [x] Invariant verified: Infrastructure Admin cannot approve operational programmes.
- [x] Invariant verified: Departmental isolation blocks cross-department mutations.
- [x] 17 of 17 automated tests passing.
- [x] Frontend builds cleanly for production.

**Verdict:** **EXIT GATE G0-02 PASSED.**  
**Next Runnable Phase:** **Phase 03: Distinctive Design System and Honest Application Shell.**
