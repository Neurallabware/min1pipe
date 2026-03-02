"""Regression test for strict standalone source_detection module."""

import sys
from pathlib import Path
import numpy as np

MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_DIR.parent))

from source_detection import run_source_detection
from _shared.fixtures import load_npz
from _shared.params import strict_default_parameters
from motion_correction import run_motion_correction

TEST_DATA = MODULE_DIR.parent / "_test_data_strict" / "source_detection" / "output.npz"
VIDEO = MODULE_DIR.parent.parent / "demo" / "demo_data.tif"


def main():
    print("=" * 60)
    print("REGRESSION TEST: source_detection standalone module")
    print("=" * 60)

    if not TEST_DATA.exists():
        raise FileNotFoundError(
            f"{TEST_DATA} not found. Run: python separation/build_strict_fixtures.py"
        )
    expected = load_npz(TEST_DATA)
    params = strict_default_parameters()
    mc = run_motion_correction(VIDEO, params, mode="strict")
    print(f"\nParameters: {params}")
    print(f"Corrected video shape: {mc.corrected_video.shape}")
    print(f"Imax shape: {mc.imax.shape}")

    result = run_source_detection(
        corrected_video=mc.corrected_video,
        imax=mc.imax,
        params=params,
        mode="strict",
    )

    checks = {
        "roifn": (result.roifn, expected["roifn"]),
        "sigfn": (result.sigfn, expected["sigfn"]),
        "seedsfn": (result.seedsfn, expected["seedsfn"]),
        "datasmth": (result.datasmth, expected["datasmth"]),
        "cutoff": (result.cutoff, expected["cutoff"]),
        "pkcutoff": (result.pkcutoff, expected["pkcutoff"]),
    }

    all_pass = True
    for name, (actual, exp) in checks.items():
        match = np.allclose(actual, exp, rtol=1e-4, atol=1e-6)
        status = "PASS" if match else "FAIL"
        if not match:
            all_pass = False
            max_diff = float(np.max(np.abs(actual - exp)))
            print(f"  [{status}] {name}: max_diff={max_diff:.2e}, shape actual={actual.shape} expected={exp.shape}")
        else:
            print(f"  [{status}] {name}: shape={actual.shape}")

    print(f"\n  n_components: {result.n_components} (expected {int(expected['n_components'])})")
    n_match = result.n_components == int(expected["n_components"])
    if not n_match:
        all_pass = False
        print(f"  [FAIL] n_components mismatch")
    else:
        print(f"  [PASS] n_components")

    print(f"\n{'=' * 60}")
    print(f"RESULT: {'SUCCESS' if all_pass else 'FAILURE'}")
    print(f"{'=' * 60}")
    return all_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
