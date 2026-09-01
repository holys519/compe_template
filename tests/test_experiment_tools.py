from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from experiment_lib import (  # noqa: E402
    evaluate_criteria,
    experiment_dir,
    next_experiment_id,
    validate_exp,
    validate_spec,
)
from run_experiment import portable_command  # noqa: E402


class ExperimentToolsTest(unittest.TestCase):
    def test_global_next_id_is_shared_by_mac_and_gpu(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "m_experiments" / "exp002").mkdir(parents=True)
            (root / "l_experiments" / "exp007").mkdir(parents=True)
            (root / "g_experiments" / "exp011").mkdir(parents=True)
            self.assertEqual(next_experiment_id(root), "exp012")

    def test_experiment_dir(self) -> None:
        root = Path("/repo")
        self.assertEqual(experiment_dir(root, "m", "exp001"), root / "m_experiments/exp001")
        self.assertEqual(experiment_dir(root, "l", "exp001"), root / "l_experiments/exp001")
        self.assertEqual(experiment_dir(root, "g", "exp001"), root / "g_experiments/exp001")

    def test_invalid_experiment_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_exp("experiment1")

    def test_criteria_are_evaluated_from_metrics_object(self) -> None:
        spec = {"success_criteria": [{"metric": "cv", "op": ">=", "value": 0.8}]}
        result = evaluate_criteria(spec, {"metrics": {"cv": 0.81}})
        self.assertTrue(result[0].passed)

    def test_spec_environment_must_match_directory(self) -> None:
        spec = {
            "id": "exp001",
            "environment": "l",
            "hypothesis": "a sufficiently detailed hypothesis",
            "success_criteria": [{"metric": "cv", "op": ">=", "value": 0.8}],
        }
        self.assertTrue(validate_spec(spec, "m", "exp001"))

    def test_run_metadata_removes_absolute_paths_and_secrets(self) -> None:
        root = (Path.cwd() / "workspace" / "project").resolve()
        command = [
            str(root.parent / "python3"),
            str(root / "train.py"),
            f"--data={root.parent / 'external' / 'train.csv'}",
            "--token",
            "secret-value",
        ]
        self.assertEqual(
            portable_command(command, root),
            [
                "<absolute>/python3",
                "train.py",
                "--data=<absolute>/train.csv",
                "--token",
                "<redacted>",
            ],
        )


if __name__ == "__main__":
    unittest.main()
