# Phase 19 - Release rehearsal, judge challenge and handover

Copy-ready implementation prompt. Run after: 00-18 complete with evidence.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md and docs/IMPLEMENTATION_STATE.md first. These files may be under the prompt-pack directory. Respect applicable repository instructions. Inspect the actual prerequisite code and evidence; if a required gate is absent, report the precise dependency and finish independent work only. Relevant blueprint sections: 40, 44-45, 52-59.

Produce a reproducible hackathon release from the working application. Do not add new major features during release hardening.

Audit every core acceptance item against actual code, passing tests and screenshots. Distinguish COMPLETE, PARTIAL, BLOCKED and NOT_RUN. Confirm 60-task monthly and up-to-30-task weekly scope actually supported by the fixture and benchmark, or report a smaller measured scope clearly. Confirm no runtime mocks, fake live badges, canned plan outputs, static KPI constants, unauthorized Railway data or external authority actions remain.

Build a clean-install and offline-demo runbook: prerequisites, pinned images/dependencies, configuration, migrations, local identity setup, explicit TEST seeding, service start, smoke checks, backup/restore and shutdown. Seeding must require an explicitly disposable TEST database; never automatically reset an existing dataset. Rehearse from a clean environment and record the exact versions/commands.

Prepare an executable challenge harness and a three-minute demonstration: source/snapshot context; monthly-to-weekly link; real solve/check; evidence for one selected and one rejected option; evaluator-chosen edit; genuine status transitions; fresh PlanDiff/metrics; human programme review. The evaluator must be able to choose a valid edit not mapped to a canned scenario response. Include a truthful unchanged outcome, no-benefit case and impossible mandatory scenario.

Create a release evidence bundle: acceptance matrix; test results; benchmark raw files; screenshots; API schema; fixture manifest/hash; rule/topology/policy versions; known limitations; dependency/licence inventory; operations runbook; architecture updates reflecting code. Update diagrams when actual implementation differs. Do not claim the blueprint itself proves runtime behavior.

Provide the demo script and recording instructions; record a video only if separately requested or explicitly part of the implementation task. Label time-compressed/precomputed footage, and retain a continuous evidence capture when recording. No fabricated latency, savings, safety or Railway approval claims.

Acceptance: a fresh user can follow the runbook; arbitrary valid edits use the same engine; all publishable plans pass the independent checker; metrics reproduce; locks and stale states behave correctly; offline rehearsal succeeds; outstanding dependencies are visible. Return the release location, actual supported scope, reproduction steps, measured results and remaining Railway pilot gates. Do not push/publish/deploy externally without task authorization.

Before finishing, update docs/IMPLEMENTATION_STATE.md, docs/ACCEPTANCE_MATRIX.md and docs/phase-reports/PHASE-19.md. Include changed behavior, actual verification commands/results, screenshots or benchmark evidence where requested, and material limitations. Do not start a later phase automatically.
