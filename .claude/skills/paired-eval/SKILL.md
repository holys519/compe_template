---
name: paired-eval
description: Pre-registered paired evaluation of an agent candidate vs a frozen baseline (same seeds, both seats, one look). Use when deciding whether a change to a game/simulation agent is a real improvement.
---
# Paired evaluation (one look)
1. Freeze artifacts: baseline B, candidate C, reference opponent R (record paths + sha). Register a fresh seed block in docs/evaluation-protocol.md BEFORE running; never reuse screen/dev seeds.
2. Run C and B against R on the same seeds, both seats. Per seed: D_s = seat-mean[M(C,R) − M(B,R)]. Sample size: 640 seeds for ±2k (per-seed sd 11-26k); for repeated confirmations use α=0.005 (800 seeds).
3. Decide once with ONE pre-declared rule (write it in spec.toml): e.g. one-sided test at alpha = 0.005 (accept if mean − t_{0.995} · se > 0), or a two-sided 95% interval (accept if lower bound > 0). Do not mix the two. State the family (how many confirmations share the alpha). Accept only if the rule passes AND guards pass (errors 0, no silent fallback, structural metrics in range, step time ≤ limit); reject if upper < 0; stop if upper < min effect; else keep B. Do not append seeds after looking.
4. Report both own-money and win/tie/loss score vs each opponent class; ties count 0.5. Write the result to the experiment README regardless of sign; publish (push/submit) only under the repository authorization policy (AGENTS.md).
5. A 20-seed screen may be used as a cheap filter only (passes ~37% of true-zero candidates); never report it as evidence.

Inputs to fix before running: metric and direction, sampling unit (seed/fold/group), opponent or fold weights, minimum relevant effect, power, alpha and family, artifact hashes (code + dependencies + parameters), runner command. Outputs: per-unit results file, machine-readable decision {accept, reject, inconclusive, harmful}, completeness check (every planned unit present exactly once), telemetry check (fallback count 0).
