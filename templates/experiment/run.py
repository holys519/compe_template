from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import tomllib
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with args.config.open("rb") as file:
        config = tomllib.load(file)

    # Replace this deterministic smoke workload with the experiment implementation.
    rng = random.Random(int(config["seed"]))
    values = [rng.random() for _ in range(int(config["sample_size"]))]
    metrics = {
        "pipeline_ok": 1.0,
        "sample_mean": statistics.fmean(values),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    document = {
        "experiment": os.environ.get("COMPE_EXP", "__EXP__"),
        "environment": os.environ.get("COMPE_ENV", "__ENV__"),
        "run_id": os.environ.get("COMPE_RUN_ID", args.output_dir.name),
        "metrics": metrics,
    }
    (args.output_dir / "metrics.json").write_text(
        json.dumps(document, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
