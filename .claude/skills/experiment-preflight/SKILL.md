---
name: experiment-preflight
description: Pre-run gate for an experiment — prove the baseline reproduces, the intervention activates and changes the intended mechanism, the evaluator measures the intended outcome, dependencies/resets/telemetry/completeness work, and the confirmation budget can answer the question. Use before any run larger than a smoke test.
---
Produce a pass/fail report (docs or runs/<exp>/preflight.md) with these checks:
1. Baseline reproduces: same artifact, same seeds → identical outputs on 2+ machines/runners (or within declared tolerance for non-deterministic stacks).
2. Intervention activates: telemetry counts show the new branch executed on representative states; diff of actions vs baseline is non-empty where expected and empty elsewhere.
3. Mechanism check: the metric the hypothesis talks about actually moves on saved states (e.g., fertilised plantings), measured by an action-level ledger, not by snapshots.
4. Environment: dependencies present on every runner (import test), no silent fallback (exceptions must be counted, not swallowed), state reset between episodes verified (run A then B equals B alone).
5. Evaluator: planned units all present exactly once; seeds registered and disjoint from screens; opponent/fold weights fixed; runner command recorded with artifact hashes.
6. Budget: with the observed variance, the planned sample size has the stated power for the minimum relevant effect; otherwise shrink the question or enlarge the sample before running.
Fail any item → fix before launching. This would have caught a missing dependency, retained-assignment bypasses and cross-episode state leaks in kaggriculture 2026-09.
