#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from datetime import date
from pathlib import Path

from experiment_lib import experiment_dir, next_experiment_id, repo_root, validate_exp


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a competition experiment")
    parser.add_argument(
        "env",
        choices=("m", "l", "g"),
        help="m=Mac, l=local RTX 3090, g=GPU cluster/cloud",
    )
    parser.add_argument("title", help="short experiment title")
    parser.add_argument("--hypothesis", required=True, help="hypothesis fixed before running")
    parser.add_argument("--change", default="TODO: describe the single main change")
    parser.add_argument("--base", default="", help="base experiment such as exp003")
    parser.add_argument("--exp", help="explicit id; default is the next global expNNN")
    return parser.parse_args()


def render_templates(destination: Path, values: dict[str, str]) -> None:
    template = repo_root() / "templates" / "experiment"
    shutil.copytree(
        template,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"),
    )
    for path in destination.rglob("*"):
        if not path.is_file():
            continue
        content = path.read_text(encoding="utf-8")
        for key, value in values.items():
            content = content.replace(f"__{key}__", value)
        path.write_text(content, encoding="utf-8")
    (destination / "run.sh").chmod(0o755)


def main() -> int:
    args = parse_args()
    root = repo_root()
    exp = validate_exp(args.exp) if args.exp else next_experiment_id(root)
    destination = experiment_dir(root, args.env, exp)
    if destination.exists():
        raise SystemExit(f"refusing to overwrite existing experiment: {destination}")
    if args.base:
        validate_exp(args.base)

    values = {
        "EXP": exp,
        "ENV": args.env,
        "TITLE": json.dumps(args.title, ensure_ascii=False),
        "HYPOTHESIS": json.dumps(args.hypothesis, ensure_ascii=False),
        "CHANGE": json.dumps(args.change, ensure_ascii=False),
        "BASE": json.dumps(args.base),
        "DATE": date.today().isoformat(),
        "DEVICE": "mps" if args.env == "m" else "cuda",
        "BATCH_SIZE": "8" if args.env == "m" else "32",
        "NUM_WORKERS": "0" if args.env == "m" else "8",
    }
    render_templates(destination, values)
    relative = destination.relative_to(root)
    print(f"created {relative}")
    print(f"next: edit {relative}/spec.toml and config.toml")
    print(f"run:  python3 scripts/run_experiment.py {args.env} {exp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
