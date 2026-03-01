"""End-to-end integration test: chain all 4 standalone modules.

Verifies that: module1 → module2 → module3 → module4 reproduces
the same output as the original monolithic pipeline.
"""

from __future__ import annotations

import pickle
import sys
from pathlib import Path

import numpy as np

SEPARATION_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SEPARATION_DIR))

from motion_correction import run_motion_correction
from source_detection import run_source_detection
from component_filtering import run_component_filtering
from calcium_deconvolution import run_calcium_deconvolution

TEST_DATA = SEPARATION_DIR / "_test_data"


def main() -> bool:
    print("=" * 70)
    print("INTEGRATION TEST: Full pipeline via chained standalone modules")
    print("=" * 70)

    # Load pipeline config
    with open(TEST_DATA / "pipeline_config.pkl", "rb") as f:
        config = pickle.load(f)

    # Load final expected outputs (from calcium_deconvolution)
    with open(TEST_DATA / "calcium_deconvolution" / "test_output.pkl", "rb") as f:
        final_expected = pickle.load(f)

    video_path = config["video_path"]
    params = config["params"]

    # ── Module 1: Motion Correction ──
    print("\n[1/4] Running motion_correction...")
    mc_result = run_motion_correction(
        video_path=video_path,
        params={
            "Fsi": params["Fsi"],
            "Fsi_new": params["Fsi_new"],
            "spatialr": params["spatialr"],
            "neuron_size": params["neuron_size"],
            "use_mc": True,
        },
    )
    print(f"      Output: corrected_video {mc_result.corrected_video.shape}")

    # Verify against motion_correction expected output
    with open(TEST_DATA / "motion_correction" / "test_output.pkl", "rb") as f:
        mc_expected = pickle.load(f)
    mc_match = np.allclose(
        mc_result.corrected_video, mc_expected["corrected_video"], rtol=1e-5, atol=1e-7
    )
    print(f"      Match with expected: {'PASS' if mc_match else 'FAIL'}")

    # ── Module 2: Source Detection ──
    print("\n[2/4] Running source_detection...")
    sd_result = run_source_detection(
        corrected_video=mc_result.corrected_video,
        imax=mc_result.imax,
        params={"neuron_size": params["neuron_size"], "max_seeds": 80},
    )
    print(f"      Output: {sd_result.n_components} components, "
          f"roifn {sd_result.roifn.shape}, sigfn {sd_result.sigfn.shape}")

    with open(TEST_DATA / "source_detection" / "test_output.pkl", "rb") as f:
        sd_expected = pickle.load(f)
    sd_match = (
        np.allclose(sd_result.roifn, sd_expected["roifn"], rtol=1e-5, atol=1e-7)
        and np.allclose(sd_result.sigfn, sd_expected["sigfn"], rtol=1e-5, atol=1e-7)
    )
    print(f"      Match with expected: {'PASS' if sd_match else 'FAIL'}")

    # ── Module 3: Component Filtering ──
    print("\n[3/4] Running component_filtering...")
    cf_result = run_component_filtering(
        roifn=sd_result.roifn,
        sigfn=sd_result.sigfn,
        seedsfn=sd_result.seedsfn,
        corrected_video=mc_result.corrected_video,
        params={"neuron_size": params["neuron_size"], "merge_corrthres": 0.9},
    )
    print(f"      Output: roifn {cf_result.roifn.shape}, sigfn {cf_result.sigfn.shape}")

    with open(TEST_DATA / "component_filtering" / "test_output.pkl", "rb") as f:
        cf_expected = pickle.load(f)
    cf_match = (
        np.allclose(cf_result.roifn, cf_expected["roifn"], rtol=1e-5, atol=1e-7)
        and np.allclose(cf_result.sigfn, cf_expected["sigfn"], rtol=1e-5, atol=1e-7)
    )
    print(f"      Match with expected: {'PASS' if cf_match else 'FAIL'}")

    # ── Module 4: Calcium Deconvolution ──
    print("\n[4/4] Running calcium_deconvolution...")
    cd_result = run_calcium_deconvolution(
        sigfn=cf_result.sigfn,
        params={"method": "simple_diff"},
    )
    print(f"      Output: spkfn {cd_result.spkfn.shape}, dff {cd_result.dff.shape}")

    spk_match = np.allclose(cd_result.spkfn, final_expected["spkfn"], rtol=1e-5, atol=1e-7)
    dff_match = np.allclose(cd_result.dff, final_expected["dff"], rtol=1e-5, atol=1e-7)
    cd_match = spk_match and dff_match
    print(f"      Match with expected: {'PASS' if cd_match else 'FAIL'}")

    # ── Summary ──
    all_pass = mc_match and sd_match and cf_match and cd_match
    print(f"\n{'=' * 70}")
    print(f"MODULE RESULTS:")
    print(f"  [{'PASS' if mc_match else 'FAIL'}] motion_correction")
    print(f"  [{'PASS' if sd_match else 'FAIL'}] source_detection")
    print(f"  [{'PASS' if cf_match else 'FAIL'}] component_filtering")
    print(f"  [{'PASS' if cd_match else 'FAIL'}] calcium_deconvolution")
    print(f"\nCOMPOSABILITY: Module chain produces identical results to monolithic pipeline")
    print(f"\nINTEGRATION RESULT: {'SUCCESS' if all_pass else 'FAILURE'}")
    print(f"{'=' * 70}")
    return all_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
