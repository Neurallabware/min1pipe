#!/usr/bin/env python3
"""Generate module parity fixture catalog."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INVENTORY = REPO_ROOT / "artifacts" / "analysis" / "matlab_inventory.json"
OUT = REPO_ROOT / "artifacts" / "parity" / "module_fixtures.json"

sys.path.insert(0, str(REPO_ROOT / "src"))


READY_CASES: dict[str, dict[str, Any]] = {
    "utilities/elements/default_parameters.m": {
        "inputs": [],
    },
    "utilities/elements/parse_type.m": {
        "inputs": ["single"],
    },
    "utilities/elements/batch_compute.m": {
        "inputs": [0],
    },
    "utilities/elements/normalize.m": {
        "inputs": [[[1.0, 2.0], [3.0, 5.0]], 4],
    },
    "utilities/elements/sigmoid.m": {
        "inputs": [[0.0, 1.0, 2.0], 2.0, 0.5],
    },
    "utilities/elements/norm_inner.m": {
        "inputs": [[[1.0, 2.0], [3.0, 4.0]], [[1.0, 0.0], [0.0, 1.0]]],
    },
}



def _module_name(matlab_path: str) -> str:
    rel = matlab_path[:-2] if matlab_path.endswith(".m") else matlab_path
    return f"min1pipe.matlab_mirror.{rel.replace('/', '.')}"



def _compute_expected(matlab_path: str, function_name: str | None, inputs: list[Any]) -> Any:
    module = importlib.import_module(_module_name(matlab_path))
    fn_name = function_name or "main"
    fn = getattr(module, fn_name)
    out = fn(*inputs)

    if hasattr(out, "tolist"):
        return out.tolist()
    if isinstance(out, tuple):
        values = []
        for item in out:
            if hasattr(item, "tolist"):
                values.append(item.tolist())
            else:
                values.append(item)
        return values
    return out



def main() -> None:
    payload = json.loads(INVENTORY.read_text())
    catalog: list[dict[str, Any]] = []

    for row in payload["files"]:
        matlab_path = row["path"]
        item: dict[str, Any] = {
            "matlab_path": matlab_path,
            "function_name": row["function_name"],
            "status": "pending",
            "reason": "fixture pending representative inputs",
            "inputs": [],
        }

        if matlab_path in READY_CASES:
            inputs = READY_CASES[matlab_path]["inputs"]
            expected = _compute_expected(matlab_path, row["function_name"], inputs)
            item.update(
                {
                    "status": "ready",
                    "reason": "",
                    "inputs": inputs,
                    "expected_outputs": expected,
                }
            )

        catalog.append(item)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(catalog, indent=2) + "\n")
    print(f"Wrote fixture catalog: {OUT}")


if __name__ == "__main__":
    main()
