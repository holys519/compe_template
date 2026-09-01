#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
from datetime import date

from experiment_lib import ENV_DIRS, experiment_dir, repo_root, validate_exp

ENV_LABELS = {
    "m": "Mac",
    "l": "local RTX 3090",
    "g": "GPU cluster/cloud",
}
ENV_ORDER = {"m": 0, "l": 1, "g": 2}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote an experiment to a larger environment")
    parser.add_argument("exp", help="experiment id such as exp003")
    parser.add_argument(
        "--from",
        "--from-env",
        dest="source_env",
        choices=tuple(ENV_DIRS),
        default="m",
        help="source environment (default: m)",
    )
    parser.add_argument(
        "--to",
        "--to-env",
        dest="target_env",
        choices=tuple(ENV_DIRS),
        help="target environment (default: m->l, l->g)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    exp = validate_exp(args.exp)
    source_env = args.source_env
    target_env = args.target_env or ("l" if source_env == "m" else "g")
    if ENV_ORDER[target_env] <= ENV_ORDER[source_env]:
        raise SystemExit(
            f"promotion must move to a larger environment: {source_env} -> {target_env}"
        )
    root = repo_root()
    source = experiment_dir(root, source_env, exp)
    destination = experiment_dir(root, target_env, exp)
    if not source.exists():
        raise SystemExit(
            f"{ENV_LABELS[source_env]} experiment does not exist: {source.relative_to(root)}"
        )
    if destination.exists():
        raise SystemExit(f"refusing to overwrite: {destination.relative_to(root)}")

    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", ".DS_Store"),
    )
    spec_path = destination / "spec.toml"
    spec = spec_path.read_text(encoding="utf-8")
    spec = re.sub(
        rf'^environment\s*=\s*"{source_env}"$',
        f'environment = "{target_env}"',
        spec,
        flags=re.MULTILINE,
    )
    promotion = (
        "\n\n[[promotions]]\n"
        f'from = "{source_env}"\n'
        f'to = "{target_env}"\n'
        f'source = "{ENV_DIRS[source_env]}/{exp}"\n'
        f'at = "{date.today().isoformat()}"\n'
    )
    spec = spec.rstrip() + promotion
    spec_path.write_text(spec, encoding="utf-8")

    config_path = destination / "config.toml"
    if config_path.exists():
        config = config_path.read_text(encoding="utf-8")
        config = re.sub(r'^device\s*=\s*"[^"]+"$', 'device = "cuda"', config, flags=re.MULTILINE)
        config = re.sub(r"^num_workers\s*=\s*0$", "num_workers = 8", config, flags=re.MULTILINE)
        config_path.write_text(config, encoding="utf-8")

    readme_path = destination / "README.md"
    readme = readme_path.read_text(encoding="utf-8").replace(
        f"- Environment: `{source_env}`", f"- Environment: `{target_env}`"
    )
    readme_path.write_text(readme, encoding="utf-8")
    (destination / "run.sh").chmod(0o755)

    relative = destination.relative_to(root)
    print(f"promoted {ENV_DIRS[source_env]}/{exp} -> {relative}")
    print("review config.toml for batch size, folds, epochs, workers, and scheduler resources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
