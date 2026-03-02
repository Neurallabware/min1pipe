"""Strict end-to-end integration test with deviation ledger."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

SEPARATION_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SEPARATION_DIR))

from _shared.fixtures import load_npz
from _shared.params import strict_default_parameters
from pipeline_strict import run_full_pipeline_strict


STRICT_ROOT = SEPARATION_DIR / "_test_data_strict"
VIDEO = SEPARATION_DIR.parent / "demo" / "demo_data.tif"
LEDGER = STRICT_ROOT / "integration_deviation_ledger.json"


def _metrics(actual: np.ndarray, expected: np.ndarray) -> dict:
    if actual.shape != expected.shape:
        return {"pass": False, "shape_actual": list(actual.shape), "shape_expected": list(expected.shape), "max_abs_dev": float("inf"), "max_rel_dev": float("inf")}
    diff = np.abs(actual - expected)
    rel = diff / np.maximum(np.abs(expected), np.finfo(np.float64).eps)
    max_abs = float(np.max(diff)) if diff.size else 0.0
    max_rel = float(np.max(rel)) if rel.size else 0.0
    ok = bool(np.allclose(actual, expected, rtol=1e-4, atol=1e-6))
    return {"pass": ok, "shape_actual": list(actual.shape), "shape_expected": list(expected.shape), "max_abs_dev": max_abs, "max_rel_dev": max_rel}


def _load_expected() -> dict[str, dict[str, np.ndarray]]:
    out: dict[str, dict[str, np.ndarray]] = {}
    for mod in ["motion_correction", "source_detection", "component_filtering", "calcium_deconvolution"]:
        p = STRICT_ROOT / mod / "output.npz"
        if not p.exists():
            raise FileNotFoundError(f"Missing strict fixture: {p}. Run: python separation/build_strict_fixtures.py")
        out[mod] = load_npz(p)
    return out


def main() -> bool:
    print("=" * 72)
    print("STRICT INTEGRATION TEST: full chained separation pipeline")
    print("=" * 72)
    expected = _load_expected()
    cfg = strict_default_parameters()
    res = run_full_pipeline_strict(VIDEO, cfg)

    actual = {
        "motion_correction": {
            "corrected_video": res.motion.corrected_video,
            "imaxy": res.motion.imaxy,
            "imaxy_pre": res.motion.imaxy_pre,
            "imaxn": res.motion.imaxn,
            "imeanf": res.motion.imeanf,
            "imax": res.motion.imax,
            "raw_score": res.motion.raw_score,
            "corr_score": res.motion.corr_score,
        },
        "source_detection": {
            "roifn": res.source.roifn,
            "sigfn": res.source.sigfn,
            "seedsfn": res.source.seedsfn,
            "datasmth": res.source.datasmth,
            "cutoff": res.source.cutoff,
            "pkcutoff": res.source.pkcutoff,
        },
        "component_filtering": {
            "roifn": res.component.roifn,
            "sigfn": res.component.sigfn,
            "seedsfn": res.component.seedsfn,
            "bgfn": res.component.bgfn,
            "bgffn": res.component.bgffn,
            "datasmth": res.component.datasmth,
            "cutoff": res.component.cutoff,
            "pkcutoff": res.component.pkcutoff,
        },
        "calcium_deconvolution": {
            "spkfn": res.deconv.spkfn,
            "dff": res.deconv.dff,
        },
    }

    ledger: dict[str, dict] = {}
    all_pass = True
    for mod, fields in actual.items():
        print(f"\n[{mod}]")
        ledger[mod] = {}
        for name, arr in fields.items():
            met = _metrics(np.asarray(arr, dtype=np.float64), np.asarray(expected[mod][name], dtype=np.float64))
            ledger[mod][name] = met
            status = "PASS" if met["pass"] else "FAIL"
            print(f"  {status:4} {name:12} max_abs={met['max_abs_dev']:.3e} max_rel={met['max_rel_dev']:.3e}")
            all_pass = all_pass and met["pass"]

    STRICT_ROOT.mkdir(parents=True, exist_ok=True)
    LEDGER.write_text(json.dumps({"pass": all_pass, "ledger": ledger}, indent=2) + "\n")
    print(f"\nDeviation ledger: {LEDGER}")
    print("\n" + "=" * 72)
    print(f"INTEGRATION RESULT: {'SUCCESS' if all_pass else 'FAILURE'}")
    print("=" * 72)
    return all_pass


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)

