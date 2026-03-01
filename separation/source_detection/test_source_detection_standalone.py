"""Regression test for standalone source_detection module."""

import pickle
import sys
from pathlib import Path
import numpy as np

MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_DIR.parent))

from source_detection import run_source_detection

TEST_DATA = MODULE_DIR.parent / "_test_data" / "source_detection"


def main():
    print("=" * 60)
    print("REGRESSION TEST: source_detection standalone module")
    print("=" * 60)

    with open(TEST_DATA / "test_input.pkl", "rb") as f:
        inputs = pickle.load(f)
    with open(TEST_DATA / "test_output.pkl", "rb") as f:
        expected = pickle.load(f)

    print(f"\nParameters: {inputs['params']}")
    print(f"Corrected video shape: {inputs['corrected_video'].shape}")
    print(f"Imax shape: {inputs['imax'].shape}")

    result = run_source_detection(
        corrected_video=inputs["corrected_video"],
        imax=inputs["imax"],
        params=inputs["params"],
    )

    checks = {
        "roifn": (result.roifn, expected["roifn"]),
        "sigfn": (result.sigfn, expected["sigfn"]),
        "seedsfn": (result.seedsfn, expected["seedsfn"]),
    }

    all_pass = True
    for name, (actual, exp) in checks.items():
        match = np.allclose(actual, exp, rtol=1e-5, atol=1e-7)
        status = "PASS" if match else "FAIL"
        if not match:
            all_pass = False
            max_diff = float(np.max(np.abs(actual - exp)))
            print(f"  [{status}] {name}: max_diff={max_diff:.2e}, shape actual={actual.shape} expected={exp.shape}")
        else:
            print(f"  [{status}] {name}: shape={actual.shape}")

    print(f"\n  n_components: {result.n_components} (expected {expected['n_components']})")
    n_match = result.n_components == expected["n_components"]
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
