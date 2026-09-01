#!/usr/bin/env python3
from __future__ import annotations

from experiment_lib import ENV_DIRS, latest_run_dir, load_json, load_toml, repo_root


def main() -> int:
    root = repo_root()
    rows: list[tuple[str, str, str, str, str]] = []
    for env, dirname in ENV_DIRS.items():
        for exp_dir in sorted((root / dirname).glob("exp*")):
            if not exp_dir.is_dir() or not (exp_dir / "spec.toml").exists():
                continue
            spec = load_toml(exp_dir / "spec.toml")
            latest = latest_run_dir(root, env, exp_dir.name)
            state = "not-run"
            decision = "-"
            if latest and (latest / "job.json").exists():
                job = load_json(latest / "job.json")
                state = str(job.get("state", "unknown"))
                decision = str(job.get("decision", "-"))
            rows.append(
                (exp_dir.name, env, str(spec.get("status", "?")), state, decision)
            )

    print("Experiment status (m=Mac, l=RTX 3090, g=GPU cluster/cloud)")
    if not rows:
        print("No experiments yet.")
        print(
            'Create one: python3 scripts/new_experiment.py m "baseline" '
            '--hypothesis "write a testable hypothesis here"'
        )
        return 0

    headers = ("EXP", "ENV", "SPEC", "LATEST RUN", "GATE")
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(5)]
    print("  ".join(headers[i].ljust(widths[i]) for i in range(5)))
    print("  ".join("-" * width for width in widths))
    env_order = {"m": 0, "l": 1, "g": 2}
    for row in sorted(rows, key=lambda item: (item[0], env_order[item[1]])):
        print("  ".join(row[i].ljust(widths[i]) for i in range(5)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
