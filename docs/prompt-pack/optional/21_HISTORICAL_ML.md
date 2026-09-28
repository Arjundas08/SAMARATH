# Optional Phase 21 - Historical-data ML feasibility and controlled model evaluation

Use MASTER_PROMPT.md and the actual pilot/data state. FUTURE ONLY. Run only when the user requests this work and representative authorized historical data, usable labels and accountable ownership exist. The absence of data is a valid reason to stop at a data-readiness report; do not train a production-looking model on invented labels.

Choose one justified first use case: task-duration quantile estimation. Verify source joins, units, task definitions, quantity known at planning time, asset/site/resource context, interventions, missing outcomes and corrections. Identify which fields existed at the planning cutoff. Exclude actual completion/output facts that would leak the future. Assess consent/access/retention constraints and subgroup coverage; do not invent a universal adequate sample size.

Create temporal training/validation/test separation and, where data allows, a location holdout. Preserve a frozen untouched test set. Compare against a transparent median-by-task-type baseline and the existing reviewed estimate policy. Evaluate quantile loss, interval coverage, underestimation, subgroup errors and downstream planning outcomes on fixed replay snapshots. Do not substitute classification accuracy for duration quality.

Only after this audit, select a modest supported model justified by data and benchmark it. No automatic XGBoost/SHAP checkbox. Explain feature limitations; feature attribution is not causal proof. Keep constraints, mandatory priority and authority decisions deterministic and owner-controlled. The model supplies estimates/scenarios, never permission or a grant.

Version datasets/features/models, document training and licensing, monitor missingness/temporal/geographic drift and retain the deterministic fallback. Integration remains shadow-only until reviewed. Compare whether predicted estimates actually improve planning decisions without degrading required coverage or violating constraints. A predictive metric gain alone is not adoption evidence.

Acceptance: reproducible authorized dataset manifest, leakage review, baseline comparison, honest holdout results and uncertainty, rollback behavior and named owner approval before operational use. If no meaningful improvement appears, retain the deterministic system and report that outcome. Update claims only to match actual measured evidence.
