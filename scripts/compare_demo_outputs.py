#!/usr/bin/env python3
"""Compare MATLAB and Python demo outputs for numeric and visual alignment."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from min1pipe.io import load_processed_mat

try:
    from skimage.metrics import peak_signal_noise_ratio, structural_similarity
except Exception:  # pragma: no cover - optional fallback path.
    peak_signal_noise_ratio = None
    structural_similarity = None


NUMERIC_TOLERANCES: dict[str, tuple[float, float]] = {
    "imaxn": (1e-3, 1e-5),
    "imaxy": (1e-3, 1e-5),
    "imax": (1e-3, 1e-5),
    "roifn": (1e-2, 1e-4),
    "sigfn": (1e-2, 1e-4),
    "seeds_c0": (0.0, 0.0),
    "raw_score": (1e-2, 1e-4),
    "corr_score": (1e-2, 1e-4),
}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matlab-dir", type=Path, required=True, help="MATLAB artifact directory")
    parser.add_argument("--python-dir", type=Path, required=True, help="Python artifact directory")
    parser.add_argument("--report-md", type=Path, required=True, help="Output markdown report path")
    parser.add_argument("--report-json", type=Path, required=True, help="Output JSON report path")
    parser.add_argument("--min-ssim", type=float, default=0.90, help="Minimum per-panel SSIM")
    parser.add_argument("--min-psnr", type=float, default=25.0, help="Minimum per-panel PSNR")
    return parser.parse_args()


def _safe_rel(diff: np.ndarray, ref: np.ndarray) -> np.ndarray:
    denom = np.maximum(np.abs(ref), np.finfo(np.float64).eps)
    return diff / denom


def _compare_arrays(name: str, ref: np.ndarray, cand: np.ndarray) -> dict[str, Any]:
    tol_rtol, tol_atol = NUMERIC_TOLERANCES[name]
    if ref.shape != cand.shape:
        return {
            "field": name,
            "status": "fail",
            "shape_ref": list(ref.shape),
            "shape_py": list(cand.shape),
            "max_abs_dev": float("inf"),
            "max_rel_dev": float("inf"),
            "rtol": tol_rtol,
            "atol": tol_atol,
            "message": "shape mismatch",
        }
    diff = np.abs(cand - ref)
    rel = _safe_rel(diff, ref)
    max_abs = float(np.nanmax(diff)) if diff.size else 0.0
    max_rel = float(np.nanmax(rel)) if rel.size else 0.0
    ok = bool(np.allclose(cand, ref, rtol=tol_rtol, atol=tol_atol, equal_nan=True))
    return {
        "field": name,
        "status": "pass" if ok else "fail",
        "shape_ref": list(ref.shape),
        "shape_py": list(cand.shape),
        "max_abs_dev": max_abs,
        "max_rel_dev": max_rel,
        "rtol": tol_rtol,
        "atol": tol_atol,
        "message": "ok" if ok else "numeric mismatch",
    }


def _load_rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)


def _resize_like(img: np.ndarray, shape_hw: tuple[int, int]) -> np.ndarray:
    h, w = shape_hw
    pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    out = pil.resize((w, h), resample=Image.Resampling.BILINEAR)
    return np.asarray(out, dtype=np.float64)


def _split_panels(img: np.ndarray) -> list[np.ndarray]:
    h, w, _ = img.shape
    hs = [0, h // 2, h]
    ws = [0, w // 3, 2 * (w // 3), w]
    out: list[np.ndarray] = []
    for r in range(2):
        for c in range(3):
            out.append(img[hs[r] : hs[r + 1], ws[c] : ws[c + 1]])
    return out


def _panel_metrics(ref_rgb: np.ndarray, cand_rgb: np.ndarray) -> tuple[float, float]:
    cand_rgb = _resize_like(cand_rgb, ref_rgb.shape[:2])
    ref_gray = ref_rgb.mean(axis=2) / 255.0
    cand_gray = cand_rgb.mean(axis=2) / 255.0

    if structural_similarity is None or peak_signal_noise_ratio is None:
        diff = np.abs(cand_gray - ref_gray)
        pseudo_ssim = float(max(0.0, 1.0 - np.mean(diff)))
        mse = float(np.mean((cand_gray - ref_gray) ** 2))
        pseudo_psnr = float("inf") if mse == 0 else float(10 * np.log10((1.0**2) / mse))
        return pseudo_ssim, pseudo_psnr

    ssim = float(structural_similarity(ref_gray, cand_gray, data_range=1.0))
    psnr = float(peak_signal_noise_ratio(ref_gray, cand_gray, data_range=1.0))
    return ssim, psnr


def _build_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Demo Alignment Report",
        "",
        f"- MATLAB dir: `{summary['matlab_dir']}`",
        f"- Python dir: `{summary['python_dir']}`",
        f"- Overall status: **{summary['status']}**",
        "",
        "## Numeric Parity",
        "",
        "| Field | Status | Shape (MATLAB) | Shape (Python) | Max Abs Dev | Max Rel Dev | Tolerance (rtol/atol) |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for row in summary["numeric"]:
        lines.append(
            "| `{}` | {} | `{}` | `{}` | {:.6g} | {:.6g} | `{:.3g}/{:.3g}` |".format(
                row["field"],
                row["status"],
                tuple(row["shape_ref"]),
                tuple(row["shape_py"]),
                row["max_abs_dev"],
                row["max_rel_dev"],
                row["rtol"],
                row["atol"],
            )
        )

    lines.extend(
        [
            "",
            "## Visual Panel Parity",
            "",
            "| Panel | Status | SSIM | PSNR |",
            "|---|---|---:|---:|",
        ]
    )
    for row in summary["visual"]:
        lines.append(
            "| {} | {} | {:.4f} | {:.3f} |".format(
                row["panel"],
                row["status"],
                row["ssim"],
                row["psnr"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    args = _parse_args()

    matlab_dir = args.matlab_dir.expanduser().resolve()
    python_dir = args.python_dir.expanduser().resolve()
    report_md = args.report_md.expanduser().resolve()
    report_json = args.report_json.expanduser().resolve()

    mat_processed = matlab_dir / "demo_data_data_processed.mat"
    py_processed = python_dir / "demo_data_data_processed.mat"
    mat_fig = matlab_dir / "demo_visualization_matlab.png"
    py_fig = python_dir / "demo_visualization_python.png"

    mat = load_processed_mat(mat_processed, source_layout="matlab")
    py = load_processed_mat(py_processed, source_layout="python")

    numeric_rows = []
    for field in NUMERIC_TOLERANCES:
        numeric_rows.append(_compare_arrays(field, np.asarray(mat[field]), np.asarray(py[field])))

    ref_img = _load_rgb(mat_fig)
    cand_img = _load_rgb(py_fig)
    ref_panels = _split_panels(ref_img)
    cand_panels = _split_panels(cand_img)

    visual_rows = []
    for idx, (ref_panel, cand_panel) in enumerate(zip(ref_panels, cand_panels, strict=True), start=1):
        ssim, psnr = _panel_metrics(ref_panel, cand_panel)
        ok = bool(ssim >= args.min_ssim and psnr >= args.min_psnr)
        visual_rows.append(
            {
                "panel": idx,
                "status": "pass" if ok else "fail",
                "ssim": ssim,
                "psnr": psnr,
                "threshold_ssim": args.min_ssim,
                "threshold_psnr": args.min_psnr,
            }
        )

    numeric_ok = all(row["status"] == "pass" for row in numeric_rows)
    visual_ok = all(row["status"] == "pass" for row in visual_rows)
    overall_ok = numeric_ok and visual_ok

    summary = {
        "status": "pass" if overall_ok else "fail",
        "matlab_dir": str(matlab_dir),
        "python_dir": str(python_dir),
        "numeric": numeric_rows,
        "visual": visual_rows,
    }

    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(summary, indent=2) + "\n")
    report_md.write_text(_build_markdown(summary) + "\n")

    print(f"Report JSON: {report_json}")
    print(f"Report Markdown: {report_md}")
    raise SystemExit(0 if overall_ok else 1)


if __name__ == "__main__":
    main()
