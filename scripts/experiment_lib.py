from __future__ import annotations

import json
import operator
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ENV_DIRS = {
    "m": "m_experiments",
    "l": "l_experiments",
    "g": "g_experiments",
}
EXP_RE = re.compile(r"exp\d{3,}[mlg]?$")   # optional env suffix (exp082m) — the strict form blocked status.py for a week in kaggriculture
OPS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}


@dataclass(frozen=True)
class CriterionResult:
    metric: str
    op: str
    expected: Any
    actual: Any
    passed: bool


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def validate_env(env: str) -> str:
    if env not in ENV_DIRS:
        raise ValueError(f"environment must be one of {sorted(ENV_DIRS)}: {env!r}")
    return env


def validate_exp(exp: str) -> str:
    if not EXP_RE.fullmatch(exp):
        raise ValueError(f"experiment id must match expNNN or expNNN[mlg]: {exp!r}")
    return exp


def experiment_dir(root: Path, env: str, exp: str) -> Path:
    return root / ENV_DIRS[validate_env(env)] / validate_exp(exp)


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as file:
        return tomllib.load(file)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def experiment_ids(root: Path) -> set[str]:
    found: set[str] = set()
    for dirname in ENV_DIRS.values():
        parent = root / dirname
        if not parent.exists():
            continue
        for path in parent.iterdir():
            if path.is_dir() and EXP_RE.fullmatch(path.name):
                found.add(path.name)
    return found


def next_experiment_id(root: Path) -> str:
    numbers = [int(re.sub(r"[mlg]$", "", exp[3:])) for exp in experiment_ids(root)]
    return f"exp{max(numbers, default=0) + 1:03d}"


def validate_spec(spec: dict[str, Any], env: str, exp: str) -> list[str]:
    problems: list[str] = []
    if spec.get("id") != exp:
        problems.append(f"spec id is {spec.get('id')!r}, expected {exp!r}")
    if spec.get("environment") != env:
        problems.append(
            f"spec environment is {spec.get('environment')!r}, expected {env!r}"
        )
    hypothesis = spec.get("hypothesis")
    if not isinstance(hypothesis, str) or len(hypothesis.strip()) < 10:
        problems.append("hypothesis must contain at least 10 characters")
    criteria = spec.get("success_criteria")
    if not isinstance(criteria, list) or not criteria:
        problems.append("at least one [[success_criteria]] entry is required")
    else:
        for index, criterion in enumerate(criteria):
            if not isinstance(criterion, dict):
                problems.append(f"success_criteria[{index}] must be a table")
                continue
            if not criterion.get("metric"):
                problems.append(f"success_criteria[{index}].metric is required")
            if criterion.get("op") not in OPS:
                problems.append(f"success_criteria[{index}].op must be one of {sorted(OPS)}")
            if "value" not in criterion:
                problems.append(f"success_criteria[{index}].value is required")
    return problems


def evaluate_criteria(
    spec: dict[str, Any], metrics_document: dict[str, Any]
) -> list[CriterionResult]:
    metrics = metrics_document.get("metrics", {})
    if not isinstance(metrics, dict):
        metrics = {}
    results: list[CriterionResult] = []
    for criterion in spec.get("success_criteria", []):
        metric = str(criterion["metric"])
        op_name = str(criterion["op"])
        expected = criterion["value"]
        actual = metrics.get(metric)
        try:
            passed = actual is not None and bool(OPS[op_name](actual, expected))
        except (KeyError, TypeError, ValueError):
            passed = False
        results.append(CriterionResult(metric, op_name, expected, actual, passed))
    return results


def latest_run_dir(root: Path, env: str, exp: str) -> Path | None:
    parent = root / "runs" / validate_env(env) / validate_exp(exp)
    if not parent.exists():
        return None
    candidates = [path for path in parent.iterdir() if path.is_dir()]
    return max(candidates, key=lambda path: path.stat().st_mtime_ns) if candidates else None
