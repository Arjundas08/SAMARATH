# Resume prompt

Continue SAMARATH from the last verified checkpoint in this repository.

Read MASTER_PROMPT.md, IMPLEMENTATION_ADDENDUM.md, DESIGN_BRIEF.md, applicable repository instructions and docs/IMPLEMENTATION_STATE.md. Inspect the actual working tree, previous phase report and failing/incomplete checks. Do not infer completion from a previous assistant's prose.

Resume the currently requested phase only. Preserve completed behavior and unrelated changes. Identify the first unmet acceptance criterion, reproduce it where possible, implement the smallest sound change and run relevant checks. Do not restart the project, replace the design system, regenerate all scaffolding or re-seed a populated database to avoid debugging.

If the prior action was blocked or NOT_RUN, verify whether the blocker is now resolved before claiming progress. Do not work around denied authorization. If the current phase is fully complete, report its evidence and the next eligible phase rather than silently executing optional pilot/ML work.

Update implementation state and the phase report with exact files, checks, evidence and remaining limits. Return a concise status grounded in actual execution.
