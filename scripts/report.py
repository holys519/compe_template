#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from experiment_lib import ENV_DIRS, latest_run_dir, load_json, load_toml, repo_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate EXPERIMENT_REPORT.md")
    parser.add_argument("--output", type=Path, help="default: EXPERIMENT_REPORT.md")
    return parser.parse_args()


def safe_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def main() -> int:
    args = parse_args()
    root = repo_root()
    output = args.output or root / "EXPERIMENT_REPORT.md"
    if not output.is_absolute():
        output = root / output
    lines = [
        "# Experiment report",
        "",
        f"Generated: {date.today().isoformat()}",
        "",
        "| Experiment | Env | Title | Latest run | Gate | Metrics |",
        "|---|---|---|---|---|---|",
    ]
    count = 0
    for env, dirname in ENV_DIRS.items():
        for exp_dir in sorted((root / dirname).glob("exp*")):
            spec_path = exp_dir / "spec.toml"
            if not exp_dir.is_dir() or not spec_path.exists():
                continue
            spec = load_toml(spec_path)
            latest = latest_run_dir(root, env, exp_dir.name)
            run_name = "-"
            gate = "-"
            metrics_text = "-"
            if latest:
                run_name = latest.name
                if (latest / "job.json").exists():
                    gate = str(load_json(latest / "job.json").get("decision", "-"))
                if (latest / "metrics.json").exists():
                    metrics = load_json(latest / "metrics.json").get("metrics", {})
                    metrics_text = json.dumps(metrics, ensure_ascii=False, sort_keys=True)
            exp_link = f"[{exp_dir.name}]({dirname}/{exp_dir.name}/README.md)"
            lines.append(
                "| "
                + " | ".join(
                    safe_cell(value)
                    for value in (
                        exp_link,
                        env,
                        spec.get("title", ""),
                        run_name,
                        gate,
                        metrics_text,
                    )
                )
                + " |"
            )
            count += 1
    if count == 0:
        lines.append("| - | - | No experiments yet | - | - | - |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {output.relative_to(root) if output.is_relative_to(root) else output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
