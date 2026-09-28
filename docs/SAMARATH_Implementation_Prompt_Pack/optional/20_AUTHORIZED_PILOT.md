# Optional Phase 20 - Authorized Railway shadow pilot

Use MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md and the existing implementation state. This phase is PILOT LATER, not part of the initial hackathon build. Execute only after the user requests pilot work and the required owner approvals and input contracts exist.

Prerequisites: core release gates pass; Railway sponsor and responsible domain/data/security owners are named; permitted datasets/interfaces, retention, access scopes and local rule applicability are documented. If these are absent, produce a precise readiness/dependency report and interface specification. Do not invent payloads, claim a live connection or use fictional records as authorized Railway data.

Implement only the approved read-only export/API adapter using the established common contract. Preserve source identifiers, versions, issue/valid timestamps, coverage manifests, error semantics and reconciliation rules. Credentials remain in approved secret storage and never enter frontend bundles, logs, public commits or prompts. Test auth failure, missing pages, partial exports, late/out-of-order events, schema drift, source outage and replay. A connector's HTTP success is not sufficient to label its data complete or fresh.

Validate actual selected-corridor topology, route/electrical footprints, compatibility, resource skills/travel, readiness, deadlines and authority observation mappings with the named owners. Record gaps as unknown and block affected publishability. Maintain TEST and Railway partitions, with no badge-only promotion.

Run retrospective and prospective shadow comparisons against the existing process on a bounded weekly scope, using monthly context. Prevent hindsight leakage in replay. Capture officer corrections, rejected recommendations, review effort, constraint violations, baseline comparisons and actual outcomes. No external operational system is controlled; proposal export remains disabled unless separately approved and contract-tested.

Implement owner-approved retention, access review, backup/restore, incident handling and audit export. Train users on infeasible, stale-data, lock-conflict and rollback cases. If recommendations are unsafe or not useful, stop their use and return to the established process while investigating.

Acceptance: signed or otherwise documented data/rule/role mapping; no unresolved critical access or false-feasibility defect; reproducible owner-agreed metrics; tested rollback; explicit go/no-go decision. Do not label the pilot successful simply because the connector works. End with actual evidence and unresolved adoption gates, without claiming Railway certification.
