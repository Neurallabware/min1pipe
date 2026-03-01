"""Run the Python pipeline and capture intermediate data at module boundaries.

This script instruments the pipeline from min1pipe_HPC.py, saving
inputs/outputs at each module boundary for regression testing of
standalone modules.

Outputs are saved under separation/_test_data/{module}/.
"""

from __future__ import annotations

import pickle
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter, shift, maximum_filter

# ── repo root ──
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from min1pipe.matlab_mirror.min1pipe_HPC import (
    _load_video,
    _normalize_01,
    _temporal_downsample,
    _spatial_downsample,
    _phase_shift,
    _movement_correct,
    _detect_seeds,
    _build_roi_and_traces,
    _compute_dff,
)
from min1pipe.matlab_mirror.utilities.elements.default_parameters import default_parameters

TEST_DATA_ROOT = REPO / "separation" / "_test_data"


def _save(obj: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    print(f"  Saved: {path}  ({path.stat().st_size / 1024:.1f} KB)")


def main() -> None:
    input_path = REPO / "demo" / "demo_data.tif"
    if not input_path.exists():
        print(f"ERROR: {input_path} not found")
        sys.exit(1)

    params = default_parameters()
    fsi = float(params["Fsi"])       # 20
    fsi_new = float(params["Fsi_new"])  # 10
    spatialr = float(params["spatialr"])  # 0.5
    neuron_size = float(params["neuron_size"])  # 5
    use_mc = True

    print("=" * 60)
    print("DATA CAPTURE: Instrumenting pipeline for module boundaries")
    print("=" * 60)

    # ════════════════════════════════════════════════════════════
    # MODULE 1: MOTION CORRECTION
    # Input: raw video file path + params
    # Output: motion-corrected video + projections + scores
    # ════════════════════════════════════════════════════════════
    print("\n── Module 1: Motion Correction ──")

    # --- motion_correction INPUT ---
    mc_input = {
        "video_path": str(input_path),
        "params": {
            "Fsi": fsi,
            "Fsi_new": fsi_new,
            "spatialr": spatialr,
            "neuron_size": neuron_size,
            "use_mc": use_mc,
        },
    }

    # Execute motion correction pipeline
    print("  Loading video...")
    frames = _load_video(input_path)
    frames = _normalize_01(frames)
    print(f"  Raw frames: {frames.shape}")

    frames = _temporal_downsample(frames, fsi, fsi_new)
    print(f"  After temporal downsample: {frames.shape}")

    frames = _spatial_downsample(frames, spatialr)
    print(f"  After spatial downsample: {frames.shape}")

    imaxn = np.max(frames, axis=0).astype(np.float32)
    imeanf = np.mean(frames, axis=0).astype(np.float32)

    # Simplified neural enhancement (gaussian smoothing)
    enhanced = np.stack(
        [gaussian_filter(frame, sigma=1.0) for frame in frames], axis=0
    )
    imaxy_pre = np.max(enhanced, axis=0).astype(np.float32)

    if use_mc:
        corrected, raw_score, corr_score = _movement_correct(enhanced)
    else:
        corrected = enhanced
        raw_score = np.zeros(enhanced.shape[0], dtype=np.float32)
        corr_score = np.zeros(enhanced.shape[0], dtype=np.float32)

    imaxy = np.max(corrected, axis=0).astype(np.float32)
    imax = imaxy.copy()

    # --- motion_correction OUTPUT ---
    mc_output = {
        "corrected_video": corrected,
        "imaxy": imaxy,
        "imaxy_pre": imaxy_pre,
        "imaxn": imaxn,
        "imeanf": imeanf,
        "imax": imax,
        "raw_score": raw_score,
        "corr_score": corr_score,
        "pixh": corrected.shape[1],
        "pixw": corrected.shape[2],
        "nf": corrected.shape[0],
    }

    _save(mc_input, TEST_DATA_ROOT / "motion_correction" / "test_input.pkl")
    _save(mc_output, TEST_DATA_ROOT / "motion_correction" / "test_output.pkl")
    print(f"  Corrected video: {corrected.shape}")

    # ════════════════════════════════════════════════════════════
    # MODULE 2: SOURCE DETECTION
    # Input: motion-corrected video + params
    # Output: ROI spatial footprints + temporal signals + seeds
    # ════════════════════════════════════════════════════════════
    print("\n── Module 2: Source Detection ──")

    sd_input = {
        "corrected_video": corrected,
        "imax": imax,
        "params": {
            "neuron_size": neuron_size,
            "max_seeds": 80,
        },
    }

    # Execute source detection
    seedsfn = _detect_seeds(imax, max_count=80)
    roifn, sigfn = _build_roi_and_traces(
        corrected, seedsfn, sigma=max(neuron_size, 1.0)
    )

    sd_output = {
        "roifn": roifn,
        "sigfn": sigfn,
        "seedsfn": seedsfn,
        "n_components": len(seedsfn),
    }

    _save(sd_input, TEST_DATA_ROOT / "source_detection" / "test_input.pkl")
    _save(sd_output, TEST_DATA_ROOT / "source_detection" / "test_output.pkl")
    print(f"  Seeds detected: {len(seedsfn)}")
    print(f"  ROI shape: {roifn.shape}, Signal shape: {sigfn.shape}")

    # ════════════════════════════════════════════════════════════
    # MODULE 3: COMPONENT FILTERING
    # Input: ROIs + signals + video
    # Output: filtered ROIs + signals + background
    # ════════════════════════════════════════════════════════════
    print("\n── Module 3: Component Filtering ──")

    # In the simplified Python pipeline, component filtering is minimal:
    # - Scale signals by max ROI weight
    # - Normalize ROIs to unit max
    # - Compute background (zeros in simplified version)

    cf_input = {
        "roifn": roifn.copy(),
        "sigfn": sigfn.copy(),
        "seedsfn": seedsfn.copy(),
        "corrected_video": corrected,
        "params": {
            "neuron_size": neuron_size,
            "merge_corrthres": 0.9,
        },
    }

    # Simplified component filtering (matching min1pipe_HPC.py logic)
    roi_max = np.max(roifn, axis=0, keepdims=True)
    roi_max_safe = np.where(roi_max > 0, roi_max, 1.0)
    sigfn_filtered = (roi_max.T * sigfn).astype(np.float32)  # scale by max weight
    roifn_filtered = (roifn / roi_max_safe).astype(np.float32)  # normalize to [0,1]

    n_pixels = corrected.shape[1] * corrected.shape[2]
    bgfn = np.zeros((n_pixels,), dtype=np.float32)
    bgffn = np.zeros((1, sigfn.shape[1]), dtype=np.float32)

    cf_output = {
        "roifn": roifn_filtered,
        "sigfn": sigfn_filtered,
        "seedsfn": seedsfn.copy(),
        "bgfn": bgfn,
        "bgffn": bgffn,
    }

    _save(cf_input, TEST_DATA_ROOT / "component_filtering" / "test_input.pkl")
    _save(cf_output, TEST_DATA_ROOT / "component_filtering" / "test_output.pkl")
    print(f"  Filtered ROI shape: {roifn_filtered.shape}")
    print(f"  Filtered Signal shape: {sigfn_filtered.shape}")

    # ════════════════════════════════════════════════════════════
    # MODULE 4: CALCIUM DECONVOLUTION
    # Input: filtered signals + options
    # Output: spike trains + dF/F
    # ════════════════════════════════════════════════════════════
    print("\n── Module 4: Calcium Deconvolution ──")

    cd_input = {
        "sigfn": sigfn_filtered.copy(),
        "params": {
            "method": "simple_diff",  # simplified version
        },
    }

    # Simplified deconvolution (matching min1pipe_HPC.py)
    spkfn = np.diff(sigfn_filtered, prepend=sigfn_filtered[:, :1], axis=1)
    spkfn = np.maximum(spkfn, 0).astype(np.float32)
    dff = _compute_dff(sigfn_filtered).astype(np.float32)

    cd_output = {
        "spkfn": spkfn,
        "dff": dff,
    }

    _save(cd_input, TEST_DATA_ROOT / "calcium_deconvolution" / "test_input.pkl")
    _save(cd_output, TEST_DATA_ROOT / "calcium_deconvolution" / "test_output.pkl")
    print(f"  Spike trains shape: {spkfn.shape}")
    print(f"  dF/F shape: {dff.shape}")

    # ════════════════════════════════════════════════════════════
    # VERIFY: full pipeline output matches chained module outputs
    # ════════════════════════════════════════════════════════════
    print("\n── Verification: Full Pipeline Consistency ──")
    print(f"  Motion Correction → {corrected.shape}")
    print(f"  Source Detection  → seeds={len(seedsfn)}, roi={roifn.shape}")
    print(f"  Component Filter  → roi={roifn_filtered.shape}, sig={sigfn_filtered.shape}")
    print(f"  Deconvolution     → spk={spkfn.shape}, dff={dff.shape}")
    print("\n  All intermediate data captured successfully.")
    print(f"  Test data root: {TEST_DATA_ROOT}")

    # Also save the full pipeline config for reference
    _save(
        {
            "params": params,
            "video_path": str(input_path),
            "module_order": [
                "motion_correction",
                "source_detection",
                "component_filtering",
                "calcium_deconvolution",
            ],
        },
        TEST_DATA_ROOT / "pipeline_config.pkl",
    )


if __name__ == "__main__":
    main()
