# Phase 15 - Human review, programme approval and audit integrity

Copy-ready implementation prompt. Run after: 02, 09-14.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 8-9, 31, 33-34.

Implement accountable human programme review and approval with atomic freshness checks.

Implement versioned lock/review/approval APIs and UI. Review actions bind exact immutable plan content, snapshot, checker result and parent lineage. Scope and delegated permission are checked server-side. Infrastructure administrator cannot approve by virtue of admin status. Rule author cannot self-approve a production rule where separation is required; TEST approval policy remains explicit.

In the approval transaction re-check the relevant current-version/freshness epoch, plan hash, VALID result, mandatory evidence, reconciliation, ETag and role. Prevent a concurrent relevant input mutation from slipping between validation and commit by using a documented transaction/locking or version-epoch strategy shared with the mutation path. A later event may mark applicability stale without rewriting the historical approval decision. Test the race, not merely sequential requests.

Locks identify task/assignment fields and authority category, not an ambiguous whole-plan Boolean. Authorized users can revise planner-controlled locks through an audited new revision. Operational reservations and completed history are not unlockable by this workflow. Show approval-block reasons and actionable navigation to the responsible evidence/input.

Persist append-only decisions and audit events containing actor/scope/time/reason, before/after references, correlation and content hash. Application-role permissions prohibit update/delete of history. If a hash chain is used, document concurrency and external anchoring limitations; it is tamper-evident within stated assumptions, not DBA-proof immutability. Generate an evidence export with provenance, status and source/version manifest. A proposal export is never an official Railway grant.

Acceptance: reviewer/approver permissions, stale version rejection, update/approval concurrency race, rejected invalid plan, missing-parent reconciliation, preserved historical decisions, duplicate command idempotency, audit linkage and server-enforced read-only metrics. Verify no grant, extension, signal-control or release endpoint exists. The UI must say programme proposal/approval accurately and keep external authority observations visually distinct.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-15.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
