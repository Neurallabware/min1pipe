"""Build strict separation fixtures and parity ledger for demo dataset."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

try:
    from separation._shared.fixtures import save_npz, write_manifest
    from separation._shared.params import strict_default_parameters
    from separation.pipeline_strict import run_full_pipeline_strict
except ModuleNotFoundError:
    from _shared.fixtures import save_npz, write_manifest
    from _shared.params import strict_default_parameters
    from pipeline_strict import run_full_pipeline_strict

try:
    from min1pipe.io import load_processed_mat
except Exception:  # pragma: no cover
    load_processed_mat = None


ROOT = Path(__file__).resolve().parent
STRICT_ROOT = ROOT / "_test_data_strict"
MATLAB_PROCESSED = ROOT.parent / "artifacts" / "golden" / "matlab" / "demo_data" / "latest" / "demo_data_data_processed.mat"
VIDEO = ROOT.parent / "demo" / "demo_data.tif"


def _deviation(actual: np.ndarray, ref: np.ndarray) -> dict[str, float]:
    if actual.shape != ref.shape:
        return {"shape_match": 0.0, "max_abs_dev": float("inf"), "max_rel_dev": float("inf")}
    diff = np.abs(actual - ref)
    rel = diff / np.maximum(np.abs(ref), np.finfo(np.float64).eps)
    return {
        "shape_match": 1.0,
        "max_abs_dev": float(np.max(diff)) if diff.size else 0.0,
        "max_rel_dev": float(np.max(rel)) if rel.size else 0.0,
    }


def main() -> None:
    cfg = strict_default_parameters()
    print("[strict-fixtures] running strict pipeline...")
    res = run_full_pipeline_strict(VIDEO, cfg, artifact_dir=STRICT_ROOT / "runtime", verbose=True)
    print("[strict-fixtures] writing fixtures...")

    save_npz(
        STRICT_ROOT / "motion_correction" / "output.npz",
        {
            "corrected_video": res.motion.corrected_video,
            "imaxy": res.motion.imaxy,
            "imaxy_pre": res.motion.imaxy_pre,
            "imaxn": res.motion.imaxn,
            "imeanf": res.motion.imeanf,
            "imax": res.motion.imax,
            "raw_score": res.motion.raw_score,
            "corr_score": res.motion.corr_score,
            "pixh": np.asarray(res.motion.pixh),
            "pixw": np.asarray(res.motion.pixw),
            "nf": np.asarray(res.motion.nf),
        },
    )
    save_npz(
        STRICT_ROOT / "source_detection" / "output.npz",
        {
            "roifn": res.source.roifn,
            "sigfn": res.source.sigfn,
            "seedsfn": res.source.seedsfn,
            "datasmth": res.source.datasmth,
            "cutoff": res.source.cutoff,
            "pkcutoff": res.source.pkcutoff,
            "n_components": np.asarray(res.source.n_components),
        },
    )
    save_npz(
        STRICT_ROOT / "component_filtering" / "output.npz",
        {
            "roifn": res.component.roifn,
            "sigfn": res.component.sigfn,
            "seedsfn": res.component.seedsfn,
            "bgfn": res.component.bgfn,
            "bgffn": res.component.bgffn,
            "datasmth": res.component.datasmth,
            "cutoff": res.component.cutoff,
            "pkcutoff": res.component.pkcutoff,
        },
    )
    save_npz(
        STRICT_ROOT / "calcium_deconvolution" / "output.npz",
        {"spkfn": res.deconv.spkfn, "dff": res.deconv.dff},
    )

    ledger: dict[str, dict] = {"status": "python_only", "fields": {}}
    if load_processed_mat is not None and MATLAB_PROCESSED.exists():
        mat = load_processed_mat(MATLAB_PROCESSED, source_layout="matlab")
        py = {
            "imaxn": res.motion.imaxn,
            "imaxy": res.motion.imaxy,
            "imax": res.motion.imax,
            "roifn": res.component.roifn,
            "sigfn": res.component.sigfn,
            "seeds_c0": res.component.seedsfn,
            "raw_score": res.motion.raw_score,
            "corr_score": res.motion.corr_score,
        }
        for k, v in py.items():
            ledger["fields"][k] = _deviation(np.asarray(v, dtype=np.float64), np.asarray(mat[k], dtype=np.float64))
        ledger["status"] = "matlab_compared"

    write_manifest(
        STRICT_ROOT / "manifest.json",
        {
            "video": str(VIDEO),
            "matlab_processed": str(MATLAB_PROCESSED),
            "status": ledger["status"],
            "params": cfg,
        },
    )
    (STRICT_ROOT / "deviation_ledger.json").write_text(json.dumps(ledger, indent=2) + "\n")
    print(f"[strict-fixtures] done: {STRICT_ROOT}")


if __name__ == "__main__":
    main()
