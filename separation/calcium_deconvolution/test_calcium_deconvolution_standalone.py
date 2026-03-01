"""Regression test for standalone calcium_deconvolution module."""

import pickle
import sys
from pathlib import Path
import numpy as np

MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_DIR.parent))

from calcium_deconvolution import run_calcium_deconvolution

TEST_DATA = MODULE_DIR.parent / "_test_data" / "calcium_deconvolution"


def main():
    print("=" * 60)
    print("REGRESSION TEST: calcium_deconvolution standalone module")
    print("=" * 60)

    with open(TEST_DATA / "test_input.pkl", "rb") as f:
        inputs = pickle.load(f)
    with open(TEST_DATA / "test_output.pkl", "rb") as f:
        expected = pickle.load(f)

    print(f"\nParameters: {inputs['params']}")
    print(f"Input Signal shape: {inputs['sigfn'].shape}")

    result = run_calcium_deconvolution(
        sigfn=inputs["sigfn"],
        params=inputs["params"],
    )

    checks = {
        "spkfn": (result.spkfn, expected["spkfn"]),
        "dff": (result.dff, expected["dff"]),
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

    print(f"\n{'=' * 60}")
    print(f"RESULT: {'SUCCESS' if all_pass else 'FAILURE'}")
    print(f"{'=' * 60}")
    return all_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
