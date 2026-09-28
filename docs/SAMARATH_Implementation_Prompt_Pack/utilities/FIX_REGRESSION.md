# Focused failure / regression repair prompt

Diagnose and fix the concrete SAMARATH failure described in my message or captured in the current failing test/output. Read MASTER_PROMPT.md, implementation state, relevant contracts and recent changes first.

Reproduce the failure using the smallest faithful case. Classify whether it is a data-contract, authorization, domain, candidate, optimizer, independent-checker, worker/concurrency, API, frontend or environment issue. Trace the actual path before modifying code. Preserve evidence about the failing snapshot/run/version and redact secrets.

Fix the root cause with a regression test that would fail before the fix. Never disable the independent checker, drop a hard constraint, turn UNKNOWN into ALLOWED, accept stale approval, replace the actual service with a mock, or hardcode the expected schedule merely to pass. If the test expectation is wrong, justify it against the documented policy and an independent example before changing it.

For UI defects, inspect the actual browser state at the affected viewport and interaction, then verify the corrected screen and keyboard behavior. For scheduling defects, use the tiny oracle or hand-calculated case and independent validation. For races, force the problematic interleaving rather than testing only a sequential happy path.

Run targeted regression and relevant integration checks, compare the previous and new behavior, and update the phase report/state. Clearly mark anything not executed. Do not perform an unrelated rewrite or claim the whole project is validated by this fix.
