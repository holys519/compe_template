from __future__ import annotations

import os
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    override = os.environ.get("COMPE_DATA_DIR")
    return Path(override).expanduser().resolve() if override else repo_root() / "data"
