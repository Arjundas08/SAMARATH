# Implementation addendum v1.1 - 26 September 2026

This pack was prepared after reviewing the generated 98-page blueprint and the subsequent feasibility assessment. It is a proposed implementation refinement. The original blueprint v1.0 remains unchanged; this addendum makes the following decisions explicit for the implementation prompts.

1. Build a bounded, demonstrable vertical slice before expanding the blueprint's large MUST list. Every listed core capability still has a delivery phase; a partial build must not be presented as the finished release.
2. Two objective profiles: PROGRAMME_IMPROVEMENT follows feasibility, mandatory work, authorized priority tiers/soft deadlines, occupation/declared operating proxy, then stability and mobilization. DISRUPTION_RECOVERY preserves hard obligations and commitments, protects required/critical coverage, and prioritizes fewer changes before marginal efficiency improvements. An explicit coverage floor and authorized priority policy prevent preserving routine assignments at the expense of required work. Version the exact lexicographic ordering in an ADR and tests. Never change it invisibly between runs.
3. Benchmark candidate construction and model size early. The 20,000-weekly-placement limit is an unvalidated guardrail, not demonstrated capacity. A naive all-pairs scan at that size examines 199,990,000 pairs. Use resource/time indexes and sparse conflict generation. If a bounded domain truncates, disclose it; do not imply complete physical-problem infeasibility.
4. Keep CP-SAT as primary, but allow a documented, correctness-tested representation change if profiling favors interval constraints or another CP-SAT encoding. Avoid building two production solvers. Tiny exhaustive cases are the comparison oracle.
5. Monthly allocation is provisional. Build actual parent-child reconciliation, not just two calendar screens. Enough aggregate hours do not establish minute-level feasibility.
6. The judge-facing strength is evidence-aware packages, precise rejection/repair, and stable response to a changed input. Frontend design serves those decisions.
7. Trained ML and real Railway integration remain gated. Current official AI/ML expectations and 2026 competition rules need confirmation; no unsupported eligibility or scoring claim is embedded in these prompts. Prototype use of CP-SAT must be called optimization, not a trained predictor.
8. No fixed timeline, winning probability or measured speedup is promised. Candidate/model/solver/checker latency and correctness must be measured on stated hardware.
9. Initial UI: seven navigation destinations with an evidence drawer, preserving the blueprint's eight workspaces without a redundant separate evidence page. Departments are filters/permissions, not duplicated products. Desktop planning is primary; compact screens support usable review and forms.
10. Design is built early and verified again after real data integration. Skeleton states and isolated component fixtures may be designed early; release figures and interactions must be backed by actual services.

## Release gates

G0: consistent contracts and development setup (00-02).
G1: labelled source inputs, geometry, rules, baseline and independent checking (03-07).
G2: real monthly/weekly solve exposed through durable APIs and rendered in the workbench (08-11).
G3: reasons, bounded repair, stable replanning, measured comparison and review/feedback (12-16).
G4: failure/security/performance evidence, visual/browser QA and reproducible offline release (17-19).

Phases 20-21 are separate optional pilot/ML work and are not authorized by completing the hackathon release. The guide supplies prompts for them so the path is explicit; execute them only when their prerequisites and user request exist.
