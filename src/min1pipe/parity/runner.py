"""Core Python parity execution and numeric comparison."""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any

import numpy as np

from .tolerances import Tolerance


@dataclass
class ParityOutcome:
    status: str
    max_abs_dev: float
    max_rel_dev: float
    message: str



def _matlab_path_to_module(matlab_path: str) -> str:
    rel = matlab_path[:-2] if matlab_path.endswith(".m") else matlab_path
    return f"min1pipe.matlab_mirror.{rel.replace('/', '.')}"



def _to_sequence(value: Any) -> list[Any]:
    if isinstance(value, tuple):
        return list(value)
    return [value]



def _as_array(x: Any) -> np.ndarray:
    if isinstance(x, np.ndarray):
        return x
    return np.asarray(x)



def compare_outputs(
    python_outputs: Any,
    reference_outputs: Any,
    tolerance: Tolerance,
) -> ParityOutcome:
    py_seq = _to_sequence(python_outputs)
    ref_seq = _to_sequence(reference_outputs)

    if len(py_seq) != len(ref_seq):
        return ParityOutcome(
            status="fail",
            max_abs_dev=float("inf"),
            max_rel_dev=float("inf"),
            message=f"Output length mismatch: python={len(py_seq)}, reference={len(ref_seq)}",
        )

    max_abs = 0.0
    max_rel = 0.0

    for py_v, ref_v in zip(py_seq, ref_seq, strict=True):
        if isinstance(py_v, dict) and isinstance(ref_v, dict):
            if py_v != ref_v:
                return ParityOutcome(
                    status="fail",
                    max_abs_dev=float("inf"),
                    max_rel_dev=float("inf"),
                    message="Dictionary output mismatch",
                )
            continue

        if isinstance(py_v, (str, bool)) and isinstance(ref_v, (str, bool)):
            if py_v != ref_v:
                return ParityOutcome(
                    status="fail",
                    max_abs_dev=float("inf"),
                    max_rel_dev=float("inf"),
                    message="Scalar output mismatch",
                )
            continue

        py_arr = _as_array(py_v)
        ref_arr = _as_array(ref_v)

        if py_arr.shape != ref_arr.shape:
            return ParityOutcome(
                status="fail",
                max_abs_dev=float("inf"),
                max_rel_dev=float("inf"),
                message=f"Shape mismatch: python={py_arr.shape}, reference={ref_arr.shape}",
            )

        diff = np.abs(py_arr - ref_arr)
        denom = np.maximum(np.abs(ref_arr), np.finfo(float).eps)
        rel = diff / denom

        max_abs = max(max_abs, float(np.nanmax(diff)) if diff.size else 0.0)
        max_rel = max(max_rel, float(np.nanmax(rel)) if rel.size else 0.0)

        if not np.allclose(py_arr, ref_arr, rtol=tolerance.rtol, atol=tolerance.atol, equal_nan=True):
            return ParityOutcome(
                status="fail",
                max_abs_dev=max_abs,
                max_rel_dev=max_rel,
                message="Numerical mismatch",
            )

    return ParityOutcome(status="pass", max_abs_dev=max_abs, max_rel_dev=max_rel, message="ok")



def run_python_case(case: dict[str, Any], tmp_path: str | None = None) -> Any:
    module_name = _matlab_path_to_module(case["matlab_path"])
    module = importlib.import_module(module_name)

    function_name = case.get("function_name")
    if not function_name:
        function_name = "main"

    if not hasattr(module, function_name):
        raise AttributeError(f"{module_name} has no callable {function_name}")

    fn = getattr(module, function_name)
    inputs = case.get("inputs", [])

    resolved_inputs = []
    for value in inputs:
        if value == "__TMP_PATH__":
            resolved_inputs.append(tmp_path)
        else:
            resolved_inputs.append(value)

    return fn(*resolved_inputs)
