"""Regression test for strict standalone motion_correction module."""

import sys
from pathlib import Path
import numpy as np

MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_DIR.parent))

from motion_correction import run_motion_correction
from _shared.fixtures import load_npz
from _shared.params import strict_default_parameters

TEST_DATA = MODULE_DIR.parent / "_test_data_strict" / "motion_correction" / "output.npz"
VIDEO = MODULE_DIR.parent.parent / "demo" / "demo_data.tif"


def main():
    print("=" * 60)
    print("REGRESSION TEST: motion_correction standalone module")
    print("=" * 60)

    if not TEST_DATA.exists():
        raise FileNotFoundError(
            f"{TEST_DATA} not found. Run: python separation/build_strict_fixtures.py"
        )
    expected = load_npz(TEST_DATA)
    params = strict_default_parameters()
    print(f"\nParameters: {params}")
    print(f"Video path: {VIDEO}")

    result = run_motion_correction(
        video_path=VIDEO,
        params=params,
        mode="strict",
    )

    # Compare outputs
    checks = {
        "corrected_video": (result.corrected_video, expected["corrected_video"]),
        "imaxy": (result.imaxy, expected["imaxy"]),
        "imaxn": (result.imaxn, expected["imaxn"]),
        "imeanf": (result.imeanf, expected["imeanf"]),
        "imax": (result.imax, expected["imax"]),
        "raw_score": (result.raw_score, expected["raw_score"]),
        "corr_score": (result.corr_score, expected["corr_score"]),
    }

    all_pass = True
    for name, (actual, exp) in checks.items():
        match = np.allclose(actual, exp, rtol=1e-4, atol=1e-6)
        status = "PASS" if match else "FAIL"
        if not match:
            all_pass = False
            max_diff = float(np.max(np.abs(actual - exp)))
            print(f"  [{status}] {name}: max_diff={max_diff:.2e}")
        else:
            print(f"  [{status}] {name}")

    print(f"\nShape checks:")
    print(f"  corrected_video: {result.corrected_video.shape} (expected {expected['corrected_video'].shape})")
    print(f"  pixh={result.pixh}, pixw={result.pixw}, nf={result.nf}")

    print(f"\n{'=' * 60}")
    print(f"RESULT: {'SUCCESS' if all_pass else 'FAILURE'}")
    print(f"{'=' * 60}")
    return all_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
