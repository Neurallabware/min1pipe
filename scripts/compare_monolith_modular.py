#!/usr/bin/env python3
"""Compare monolithic and modular capture artifacts for parity QA."""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

try:
    from skimage.metrics import structural_similarity
except Exception:  # pragma: no cover
    structural_similarity = None

BOUNDARY_FIELDS = [
    "motion__frames_ds",
    "motion__imaxn",
    "motion__imeanf",
    "motion__imaxy_pre",
    "motion__corrected_video",
    "motion__raw_score",
    "motion__corr_score",
    "motion__imax",
    "source__roifn",
    "source__sigfn",
    "source__seedsfn",
    "component__roifn",
    "component__sigfn",
    "component__seedsfn",
    "component__bgfn",
    "component__bgffn",
    "deconv__spkfn",
    "deconv__dff",
]


@dataclass
class Tol:
    rtol: float = 1e-4
    atol: float = 1e-6


def _load_manifest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _capture_map(manifest: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for row in manifest.get("captures", []):
        out[(row["dataset_root"], row["file_rel"])] = row
    return out


def _corrcoef(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 2 or b.size < 2:
        return 1.0
    aa = a.reshape(-1)
    bb = b.reshape(-1)
    if np.allclose(aa, aa[0]) or np.allclose(bb, bb[0]):
        return 1.0 if np.allclose(aa, bb) else 0.0
    c = np.corrcoef(aa, bb)
    return float(c[0, 1])


def _ssim_if_image(a: np.ndarray, b: np.ndarray) -> float | None:
    if structural_similarity is None:
        return None
    if a.shape != b.shape:
        return None
    if a.ndim not in (2, 3):
        return None
    try:
        if a.ndim == 2:
            dr = float(max(np.max(a), np.max(b)) - min(np.min(a), np.min(b)))
            dr = dr if dr > 0 else 1.0
            return float(structural_similarity(a, b, data_range=dr))
        # frame-wise SSIM mean
        vals: list[float] = []
        for i in range(a.shape[0]):
            dr = float(max(np.max(a[i]), np.max(b[i])) - min(np.min(a[i]), np.min(b[i])))
            dr = dr if dr > 0 else 1.0
            vals.append(float(structural_similarity(a[i], b[i], data_range=dr)))
        return float(np.mean(vals)) if vals else None
    except Exception:
        return None


def _metrics(actual: np.ndarray, expected: np.ndarray, tol: Tol) -> dict[str, Any]:
    if actual.shape != expected.shape:
        return {
            "pass": False,
            "shape_actual": list(actual.shape),
            "shape_expected": list(expected.shape),
            "max_abs_err": float("inf"),
            "max_rel_err": float("inf"),
            "corrcoef": 0.0,
            "ssim": None,
        }
    diff = np.abs(actual - expected)
    rel = diff / np.maximum(np.abs(expected), np.finfo(np.float64).eps)
    ok = bool(np.allclose(actual, expected, rtol=tol.rtol, atol=tol.atol))
    return {
        "pass": ok,
        "shape_actual": list(actual.shape),
        "shape_expected": list(expected.shape),
        "max_abs_err": float(np.max(diff)) if diff.size else 0.0,
        "max_rel_err": float(np.max(rel)) if rel.size else 0.0,
        "corrcoef": _corrcoef(actual, expected),
        "ssim": _ssim_if_image(actual, expected),
    }


def _load_npz(path: str | Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as data:
        return {k: data[k] for k in data.files}


def _first_divergence(rows: list[dict[str, Any]]) -> str:
    for row in rows:
        if not row["pass"]:
            return row["field"]
    return "<none>"


def _compare_variant(
    monolith_manifest: dict[str, Any],
    modular_manifest: dict[str, Any],
    tol: Tol,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    monolith = _capture_map(monolith_manifest)
    modular = _capture_map(modular_manifest)
    rows: list[dict[str, Any]] = []
    summary: list[dict[str, Any]] = []

    common_keys = sorted(set(monolith.keys()) & set(modular.keys()))
    for key in common_keys:
        mrow = monolith[key]
        brow = modular[key]
        mcap = _load_npz(mrow["capture_npz"])
        bcap = _load_npz(brow["capture_npz"])
        per_file_rows: list[dict[str, Any]] = []
        for field in BOUNDARY_FIELDS:
            if field not in mcap or field not in bcap:
                per_file_rows.append(
                    {
                        "dataset_root": key[0],
                        "file_rel": key[1],
                        "variant": f"{modular_manifest['mode']}_{modular_manifest['serialization']}",
                        "field": field,
                        "pass": False,
                        "max_abs_err": float("inf"),
                        "max_rel_err": float("inf"),
                        "corrcoef": 0.0,
                        "ssim": None,
                        "shape_actual": [],
                        "shape_expected": [],
                        "reason": "missing_field",
                    }
                )
                continue
            met = _metrics(
                np.asarray(bcap[field], dtype=np.float64),
                np.asarray(mcap[field], dtype=np.float64),
                tol,
            )
            per_file_rows.append(
                {
                    "dataset_root": key[0],
                    "file_rel": key[1],
                    "variant": f"{modular_manifest['mode']}_{modular_manifest['serialization']}",
                    "field": field,
                    "pass": met["pass"],
                    "max_abs_err": met["max_abs_err"],
                    "max_rel_err": met["max_rel_err"],
                    "corrcoef": met["corrcoef"],
                    "ssim": met["ssim"],
                    "shape_actual": met["shape_actual"],
                    "shape_expected": met["shape_expected"],
                    "reason": "",
                }
            )
        rows.extend(per_file_rows)
        summary.append(
            {
                "dataset_root": key[0],
                "file_rel": key[1],
                "variant": f"{modular_manifest['mode']}_{modular_manifest['serialization']}",
                "all_pass": all(r["pass"] for r in per_file_rows),
                "first_divergence": _first_divergence(per_file_rows),
            }
        )
    return rows, summary


def _serialization_probe(
    manifest_none: dict[str, Any],
    manifest_rt: dict[str, Any],
    tol: Tol,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    none_map = _capture_map(manifest_none)
    rt_map = _capture_map(manifest_rt)
    for key in sorted(set(none_map.keys()) & set(rt_map.keys())):
        ncap = _load_npz(none_map[key]["capture_npz"])
        rcap = _load_npz(rt_map[key]["capture_npz"])
        for field in BOUNDARY_FIELDS:
            if field not in ncap or field not in rcap:
                continue
            met = _metrics(np.asarray(rcap[field], dtype=np.float64), np.asarray(ncap[field], dtype=np.float64), tol)
            rows.append(
                {
                    "dataset_root": key[0],
                    "file_rel": key[1],
                    "probe_variant": manifest_rt["serialization"],
                    "field": field,
                    "pass": met["pass"],
                    "max_abs_err": met["max_abs_err"],
                    "max_rel_err": met["max_rel_err"],
                    "corrcoef": met["corrcoef"],
                }
            )
    return rows


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-dir", type=Path, required=True)
    p.add_argument("--rtol", type=float, default=1e-4)
    p.add_argument("--atol", type=float, default=1e-6)
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    run_dir = args.run_dir.expanduser().resolve()
    tol = Tol(rtol=args.rtol, atol=args.atol)

    mono_path = run_dir / "manifest_monolith.json"
    if not mono_path.exists():
        raise FileNotFoundError(mono_path)

    modular_manifests = sorted(run_dir.glob("manifest_modular_*.json"))
    if not modular_manifests:
        raise FileNotFoundError(f"No modular manifests found under {run_dir}")

    monolith_manifest = _load_manifest(mono_path)

    all_rows: list[dict[str, Any]] = []
    all_summary: list[dict[str, Any]] = []
    by_variant: dict[str, dict[str, Any]] = {}

    loaded_modular: dict[str, dict[str, Any]] = {}
    for path in modular_manifests:
        manifest = _load_manifest(path)
        variant = f"{manifest['mode']}_{manifest['serialization']}"
        loaded_modular[variant] = manifest
        rows, summary = _compare_variant(monolith_manifest, manifest, tol)
        all_rows.extend(rows)
        all_summary.extend(summary)
        by_variant[variant] = {
            "manifest": str(path),
            "rows": len(rows),
            "files": len(summary),
            "pass": all(s["all_pass"] for s in summary),
            "first_divergences": summary,
        }

    probe_rows: list[dict[str, Any]] = []
    if "parity_none" in loaded_modular:
        for probe_variant in ("parity_pickle", "parity_h5"):
            if probe_variant in loaded_modular:
                probe_rows.extend(_serialization_probe(loaded_modular["parity_none"], loaded_modular[probe_variant], tol))

    report_json = run_dir / "discrepancy_report.json"
    report_csv = run_dir / "discrepancy_report.csv"
    report_md = run_dir / "discrepancy_report.md"

    payload = {
        "run_dir": str(run_dir),
        "tolerance": {"rtol": tol.rtol, "atol": tol.atol},
        "variants": by_variant,
        "rows": all_rows,
        "summary": all_summary,
        "serialization_probe": probe_rows,
        "skipped": monolith_manifest.get("skipped", []),
    }
    report_json.write_text(json.dumps(payload, indent=2) + "\n")

    with report_csv.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "variant",
                "dataset_root",
                "file_rel",
                "field",
                "pass",
                "max_abs_err",
                "max_rel_err",
                "corrcoef",
                "ssim",
                "shape_actual",
                "shape_expected",
                "reason",
            ],
        )
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    md: list[str] = [
        "# Monolithic vs Modular Discrepancy Report",
        "",
        f"- Run dir: `{run_dir}`",
        f"- Tolerance: `rtol={tol.rtol}`, `atol={tol.atol}`",
        "",
        "## Variant Summary",
        "",
        "| Variant | Files | Overall |",
        "|---|---:|---|",
    ]
    for variant, info in sorted(by_variant.items()):
        md.append(f"| `{variant}` | {info['files']} | {'PASS' if info['pass'] else 'FAIL'} |")

    md += ["", "## First Divergence by File", "", "| Variant | Dataset | File | First Divergence | All Pass |", "|---|---|---|---|---|"]
    for row in all_summary:
        md.append(
            f"| `{row['variant']}` | `{row['dataset_root']}` | `{row['file_rel']}` | `{row['first_divergence']}` | {'PASS' if row['all_pass'] else 'FAIL'} |"
        )

    md += ["", "## Boundary Metrics", "", "| Variant | File | Field | Pass | Max Abs Err | Max Rel Err | Corr | SSIM |", "|---|---|---|---|---:|---:|---:|---:|"]
    for row in all_rows:
        ssim_txt = "n/a" if row["ssim"] is None else f"{row['ssim']:.6f}"
        md.append(
            f"| `{row['variant']}` | `{row['file_rel']}` | `{row['field']}` | {'PASS' if row['pass'] else 'FAIL'} | {row['max_abs_err']:.6g} | {row['max_rel_err']:.6g} | {row['corrcoef']:.6g} | {ssim_txt} |"
        )

    if payload["skipped"]:
        md += ["", "## Skipped Files", "", "| File | Reason |", "|---|---|"]
        for row in payload["skipped"]:
            md.append(f"| `{row['file']}` | `{row['reason']}` |")

    if probe_rows:
        md += ["", "## Serialization Probe (vs parity_none)", "", "| Probe | File | Field | Pass | Max Abs Err | Max Rel Err | Corr |", "|---|---|---|---|---:|---:|---:|"]
        for row in probe_rows:
            md.append(
                f"| `{row['probe_variant']}` | `{row['file_rel']}` | `{row['field']}` | {'PASS' if row['pass'] else 'FAIL'} | {row['max_abs_err']:.6g} | {row['max_rel_err']:.6g} | {row['corrcoef']:.6g} |"
            )

    report_md.write_text("\n".join(md) + "\n")

    print(f"[compare] json: {report_json}")
    print(f"[compare] csv:  {report_csv}")
    print(f"[compare] md:   {report_md}")


if __name__ == "__main__":
    main()
