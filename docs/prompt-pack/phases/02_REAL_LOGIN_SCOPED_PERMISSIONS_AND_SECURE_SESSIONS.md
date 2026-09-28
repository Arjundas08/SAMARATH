# Phase 02 - Real login, scoped permissions and secure sessions

Copy-ready implementation prompt. Run after: 01.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 8-9, 31, 33-34.

Implement real local identity and authorization before adding business write actions.

Use Keycloak OIDC authorization-code flow with PKCE, state/nonce and backend token handling. Browser uses an HttpOnly, Secure, appropriate SameSite session cookie through a same-origin proxy; do not put tokens in localStorage. Validate issuer, audience, signature, expiry and callback state. Implement login, logout, session expiry and rotation using maintained libraries. Document local TLS setup and any explicit localhost-only development exception; no demo bypass must survive a release configuration.

Seed fictional functional roles: departmental planners, coordinator, operating reviewer, delegated programme approver, integration operator, rule author/approver, auditor and infrastructure administrator. Use permissions plus department and territory scopes; infrastructure administrator is not automatically a business approver. Model explicit scope grants for shared boundary resources. Never trust role/territory/mode sent from the client.

Implement GET /api/v1/session and authorization dependencies for API/domain actions. Enforce row access in services and add PostgreSQL RLS where designed, with a non-owner/non-bypass app role. Ensure connection-pool reuse cannot leak another request's scope: use transaction-local settings and test cleanup. Workers must operate on authorized scoped jobs rather than granting themselves global business access.

Add CSRF protection to cookie-authenticated mutations, constrained CORS, session limits and redacted authentication logs. Separate credentials for migration, API and worker as appropriate. Keep TEST bootstrap users local and clearly documented; no production default password. Do not expose client secrets in frontend assets.

Acceptance tests: successful login and logout; expired session; invalid callback state; unauthenticated 401; forbidden role action; cross-territory access with no record disclosure; forbidden cross-department mutation; administrator cannot approve; connection reuse does not cross scopes. Browser tests must use real local authentication, not a mocked role dropdown. Return permission matrix and actual test evidence.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-02.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
