#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from experiment_lib import (
    evaluate_criteria,
    experiment_dir,
    load_json,
    load_toml,
    repo_root,
    validate_exp,
    validate_spec,
)


def parse_args() -> argparse.Namespace:
    raw_args = sys.argv[1:]
    command: list[str] = []
    if "--" in raw_args:
        separator = raw_args.index("--")
        command = raw_args[separator + 1 :]
        raw_args = raw_args[:separator]
    parser = argparse.ArgumentParser(description="Run an experiment with reproducible metadata")
    parser.add_argument("env", choices=("m", "l", "g"))
    parser.add_argument("exp")
    parser.add_argument("--run-id", help="default: UTC timestamp")
    args = parser.parse_args(raw_args)
    args.command = command
    return args


def now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def git_value(root: Path, *args: str) -> str | None:
    result = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def portable_command(command: list[str], root: Path) -> list[str]:
    """Remove machine-specific absolute paths and CLI secrets from public metadata."""
    secret_flags = {"--api-key", "--password", "--secret", "--token"}
    portable: list[str] = []
    redact_next = False
    for index, argument in enumerate(command):
        if redact_next:
            portable.append("<redacted>")
            redact_next = False
            continue

        flag, separator, value = argument.partition("=")
        if flag.lower() in secret_flags:
            if separator:
                portable.append(f"{flag}=<redacted>")
            else:
                portable.append(argument)
                redact_next = True
            continue

        if index == 0 and argument == sys.executable:
            portable.append("python")
            continue

        candidate = Path(value if separator else argument)
        if candidate.is_absolute():
            try:
                rendered = str(candidate.relative_to(root))
            except ValueError:
                rendered = f"<absolute>/{candidate.name}"
            portable.append(f"{flag}={rendered}" if separator else rendered)
        else:
            portable.append(argument)
    return portable


def main() -> int:
    args = parse_args()
    root = repo_root()
    exp = validate_exp(args.exp)
    exp_dir = experiment_dir(root, args.env, exp)
    if not exp_dir.exists():
        raise SystemExit(f"experiment does not exist: {exp_dir.relative_to(root)}")

    spec_path = exp_dir / "spec.toml"
    config_path = exp_dir / "config.toml"
    spec = load_toml(spec_path)
    problems = validate_spec(spec, args.env, exp)
    if problems:
        raise SystemExit("invalid spec.toml:\n- " + "\n- ".join(problems))

    run_id = args.run_id or datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", run_id):
        raise SystemExit("run id may contain only letters, numbers, dash, underscore, and dot")
    run_dir = root / "runs" / args.env / exp / run_id
    if run_dir.exists():
        raise SystemExit(f"refusing to overwrite existing run: {run_dir.relative_to(root)}")
    run_dir.mkdir(parents=True)
    shutil.copy2(spec_path, run_dir / "spec.toml")
    if config_path.exists():
        shutil.copy2(config_path, run_dir / "config.toml")

    command = list(args.command)
    if not command:
        run_py = exp_dir / "run.py"
        if not run_py.exists():
            raise SystemExit(f"default entrypoint is missing: {run_py.relative_to(root)}")
        command = [
            sys.executable,
            str(run_py),
            "--config",
            str(config_path),
            "--output-dir",
            str(run_dir),
        ]

    commit = git_value(root, "rev-parse", "HEAD")
    dirty = bool(git_value(root, "status", "--porcelain")) if commit else None
    job: dict[str, Any] = {
        "experiment": exp,
        "environment": args.env,
        "run_id": run_id,
        "state": "running",
        "started_at": now_iso(),
        "command": portable_command(command, root),
        "cwd": ".",
        "git_commit": commit,
        "git_dirty": dirty,
        "host": {
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
    }
    job_path = run_dir / "job.json"
    write_json(job_path, job)

    child_env = os.environ.copy()
    src_path = str(root / "src")
    child_env["PYTHONPATH"] = (
        src_path + os.pathsep + child_env["PYTHONPATH"]
        if child_env.get("PYTHONPATH")
        else src_path
    )
    child_env.update(
        {
            "COMPE_ENV": args.env,
            "COMPE_EXP": exp,
            "COMPE_RUN_ID": run_id,
            "COMPE_RUN_DIR": str(run_dir),
        }
    )

    print(f"run: {args.env}/{exp}/{run_id}")
    print("command:", " ".join(command))
    log_path = run_dir / "stdout.log"
    started = time.perf_counter()
    try:
        with log_path.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                command,
                cwd=root,
                env=child_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            assert process.stdout is not None
            for line in process.stdout:
                print(line, end="")
                log.write(line)
            returncode = process.wait()
    except OSError as exc:
        job.update(
            {
                "state": "failed",
                "finished_at": now_iso(),
                "duration_sec": round(time.perf_counter() - started, 3),
                "returncode": None,
                "error": f"could not start command: {exc}",
            }
        )
        write_json(job_path, job)
        print(f"FAILED: {job['error']}", file=sys.stderr)
        return 127

    job["finished_at"] = now_iso()
    job["duration_sec"] = round(time.perf_counter() - started, 3)
    job["returncode"] = returncode
    metrics_path = run_dir / "metrics.json"
    metrics_document: dict[str, Any] | None = None
    metrics_error: str | None = None
    if returncode == 0:
        try:
            metrics_document = load_json(metrics_path)
            if not isinstance(metrics_document.get("metrics"), dict):
                raise ValueError("top-level 'metrics' must be an object")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            metrics_error = str(exc)

    if returncode != 0 or metrics_error:
        job["state"] = "failed"
        if metrics_error:
            job["error"] = f"invalid metrics.json: {metrics_error}"
        write_json(job_path, job)
        print(f"FAILED: see {log_path.relative_to(root)}", file=sys.stderr)
        if metrics_error:
            print(job["error"], file=sys.stderr)
        return returncode or 2

    assert metrics_document is not None
    criteria = evaluate_criteria(spec, metrics_document)
    job["state"] = "completed"
    job["criteria"] = [result.__dict__ for result in criteria]
    job["decision"] = "pass" if criteria and all(result.passed for result in criteria) else "fail"
    write_json(job_path, job)
    print(f"completed: decision={job['decision']} metrics={metrics_document['metrics']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
