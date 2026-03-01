"""Pytest configuration and parity result logging."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import sys

import pytest

RUNTIME_DIR = Path(__file__).resolve().parents[1] / "artifacts" / "parity" / "runtime"
SRC_DIR = Path(__file__).resolve().parents[1] / "src"
PARITY_RESULTS: list[dict[str, Any]] = []

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture
def record_parity_result() -> Any:
    def _record(row: dict[str, Any]) -> None:
        PARITY_RESULTS.append(row)

    return _record



def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    out_json = RUNTIME_DIR / "parity_results.json"
    out_md = RUNTIME_DIR / "parity_results.md"

    out_json.write_text(json.dumps(PARITY_RESULTS, indent=2) + "\n")

    lines = [
        "# Parity Results",
        "",
        "| MATLAB Path | Status | Max Abs Dev | Max Rel Dev | Message |",
        "|---|---:|---:|---:|---|",
    ]
    for row in PARITY_RESULTS:
        lines.append(
            "| `{}` | {} | {} | {} | {} |".format(
                row.get("matlab_path", ""),
                row.get("status", ""),
                row.get("max_abs_dev", ""),
                row.get("max_rel_dev", ""),
                row.get("message", "").replace("|", "\\|"),
            )
        )

    out_md.write_text("\n".join(lines) + "\n")
