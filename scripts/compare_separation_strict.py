#!/usr/bin/env python3
"""Compare strict separation runtime outputs against strict fixtures (+ optional MATLAB)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def _parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--strict-root", type=Path, required=True)
    p.add_argument("--runtime-npz", type=Path, required=True)
    p.add_argument("--report-md", type=Path, required=True)
    p.add_argument("--report-json", type=Path, required=True)
    p.add_argument("--matlab-processed", type=Path, default=None)
    return p.parse_args()


def _metrics(a: np.ndarray, b: np.ndarray, rtol: float, atol: float) -> dict:
    if a.shape != b.shape:
        return {"status": "fail", "shape_a": list(a.shape), "shape_b": list(b.shape), "max_abs_dev": float("inf"), "max_rel_dev": float("inf")}
    diff = np.abs(a - b)
    rel = diff / np.maximum(np.abs(b), np.finfo(np.float64).eps)
    ok = bool(np.allclose(a, b, rtol=rtol, atol=atol))
    return {
        "status": "pass" if ok else "fail",
        "shape_a": list(a.shape),
        "shape_b": list(b.shape),
        "max_abs_dev": float(np.max(diff)) if diff.size else 0.0,
        "max_rel_dev": float(np.max(rel)) if rel.size else 0.0,
        "rtol": rtol,
        "atol": atol,
    }


def main() -> None:
    args = _parse()
    strict_root = args.strict_root.expanduser().resolve()
    runtime_npz = args.runtime_npz.expanduser().resolve()

    runtime = dict(np.load(runtime_npz, allow_pickle=False))
    refs = {
        "motion_correction": dict(np.load(strict_root / "motion_correction" / "output.npz", allow_pickle=False)),
        "source_detection": dict(np.load(strict_root / "source_detection" / "output.npz", allow_pickle=False)),
        "component_filtering": dict(np.load(strict_root / "component_filtering" / "output.npz", allow_pickle=False)),
        "calcium_deconvolution": dict(np.load(strict_root / "calcium_deconvolution" / "output.npz", allow_pickle=False)),
    }

    checks = {
        "imaxn": refs["motion_correction"]["imaxn"],
        "imaxy": refs["motion_correction"]["imaxy"],
        "imax": refs["motion_correction"]["imax"],
        "roifn": refs["component_filtering"]["roifn"],
        "sigfn": refs["component_filtering"]["sigfn"],
        "seedsfn": refs["component_filtering"]["seedsfn"],
        "bgfn": refs["component_filtering"]["bgfn"],
        "bgffn": refs["component_filtering"]["bgffn"],
        "raw_score": refs["motion_correction"]["raw_score"],
        "corr_score": refs["motion_correction"]["corr_score"],
        "spkfn": refs["calcium_deconvolution"]["spkfn"],
        "dff": refs["calcium_deconvolution"]["dff"],
    }
    rows = []
    for key, ref in checks.items():
        rows.append({"field": key, **_metrics(np.asarray(runtime[key], dtype=np.float64), np.asarray(ref, dtype=np.float64), 1e-4, 1e-6)})
    all_ok = all(r["status"] == "pass" for r in rows)

    matlab_rows = []
    if args.matlab_processed is not None and args.matlab_processed.exists():
        try:
            from min1pipe.io import load_processed_mat

            mat = load_processed_mat(args.matlab_processed, source_layout="matlab")
            for key in ["imaxn", "imaxy", "imax", "roifn", "sigfn", "raw_score", "corr_score"]:
                if key not in runtime or key not in mat:
                    continue
                matlab_rows.append({"field": key, **_metrics(np.asarray(runtime[key], dtype=np.float64), np.asarray(mat[key], dtype=np.float64), 5e-2, 1e-2)})
        except Exception as exc:  # pragma: no cover
            matlab_rows.append({"field": "matlab_compare", "status": "fail", "error": str(exc)})

    summary = {"status": "pass" if all_ok else "fail", "strict_rows": rows, "matlab_rows": matlab_rows}
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(summary, indent=2) + "\n")

    md = [
        "# Separation Strict Gate Report",
        "",
        f"- Overall status: **{summary['status']}**",
        "",
        "## Strict Fixture Parity",
        "",
        "| Field | Status | Max Abs Dev | Max Rel Dev |",
        "|---|---|---:|---:|",
    ]
    for r in rows:
        md.append(f"| `{r['field']}` | {r['status']} | {r['max_abs_dev']:.6g} | {r['max_rel_dev']:.6g} |")
    if matlab_rows:
        md += ["", "## MATLAB Cross-Reference (Optional)", "", "| Field | Status | Max Abs Dev | Max Rel Dev |", "|---|---|---:|---:|"]
        for r in matlab_rows:
            if "max_abs_dev" in r:
                md.append(f"| `{r['field']}` | {r['status']} | {r['max_abs_dev']:.6g} | {r['max_rel_dev']:.6g} |")
            else:
                md.append(f"| `{r['field']}` | fail | n/a | n/a |")
    args.report_md.write_text("\n".join(md) + "\n")
    raise SystemExit(0 if all_ok else 1)


if __name__ == "__main__":
    main()

