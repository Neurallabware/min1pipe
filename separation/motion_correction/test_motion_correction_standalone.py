"""Regression test for standalone motion_correction module."""

import pickle
import sys
from pathlib import Path
import numpy as np

# Ensure we import from THIS directory, not the parent codebase
MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_DIR.parent))

from motion_correction import run_motion_correction

TEST_DATA = MODULE_DIR.parent / "_test_data" / "motion_correction"


def main():
    print("=" * 60)
    print("REGRESSION TEST: motion_correction standalone module")
    print("=" * 60)

    with open(TEST_DATA / "test_input.pkl", "rb") as f:
        inputs = pickle.load(f)
    with open(TEST_DATA / "test_output.pkl", "rb") as f:
        expected = pickle.load(f)

    print(f"\nParameters: {inputs['params']}")
    print(f"Video path: {inputs['video_path']}")

    result = run_motion_correction(
        video_path=inputs["video_path"],
        params=inputs["params"],
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
        match = np.allclose(actual, exp, rtol=1e-5, atol=1e-7)
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
