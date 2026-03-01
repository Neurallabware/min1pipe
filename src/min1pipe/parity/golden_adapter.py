"""Golden-artifact loader for parity tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_fixture_catalog(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text())


def fixture_by_path(catalog: list[dict[str, Any]], matlab_path: str) -> dict[str, Any] | None:
    for row in catalog:
        if row.get("matlab_path") == matlab_path:
            return row
    return None
