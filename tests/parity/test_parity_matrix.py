"""Per-module parity tests for MATLAB-to-Python mapping."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from min1pipe.parity.runner import compare_outputs, run_python_case
from min1pipe.parity.tolerances import get_tolerance

FIXTURE_CATALOG = Path(__file__).resolve().parents[2] / "artifacts" / "parity" / "module_fixtures.json"



def _load_cases() -> list[dict[str, Any]]:
    return json.loads(FIXTURE_CATALOG.read_text())


CASES = _load_cases()


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["matlab_path"])
def test_module_parity(case: dict[str, Any], tmp_path: Path, record_parity_result: Any) -> None:
    status = case.get("status", "pending")
    matlab_path = case["matlab_path"]

    if status != "ready":
        record_parity_result(
            {
                "matlab_path": matlab_path,
                "status": "skip",
                "max_abs_dev": "",
                "max_rel_dev": "",
                "message": case.get("reason", "fixture not ready"),
            }
        )
        pytest.skip(case.get("reason", "fixture not ready"))

    py_output = run_python_case(case, tmp_path=str(tmp_path))
    ref_output = case.get("expected_outputs")
    tol = get_tolerance(matlab_path)
    outcome = compare_outputs(py_output, ref_output, tol)

    record_parity_result(
        {
            "matlab_path": matlab_path,
            "status": outcome.status,
            "max_abs_dev": outcome.max_abs_dev,
            "max_rel_dev": outcome.max_rel_dev,
            "message": outcome.message,
        }
    )

    assert outcome.status == "pass", f"{matlab_path}: {outcome.message}"
