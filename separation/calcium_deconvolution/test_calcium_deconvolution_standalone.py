"""Regression test for strict standalone calcium_deconvolution module."""

import sys
from pathlib import Path
import numpy as np

MODULE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MODULE_DIR.parent))

from calcium_deconvolution import run_calcium_deconvolution
from _shared.fixtures import load_npz
from _shared.params import strict_default_parameters
from motion_correction import run_motion_correction
from source_detection import run_source_detection
from component_filtering import run_component_filtering

TEST_DATA = MODULE_DIR.parent / "_test_data_strict" / "calcium_deconvolution" / "output.npz"
VIDEO = MODULE_DIR.parent.parent / "demo" / "demo_data.tif"


def main():
    print("=" * 60)
    print("REGRESSION TEST: calcium_deconvolution standalone module")
    print("=" * 60)

    if not TEST_DATA.exists():
        raise FileNotFoundError(
            f"{TEST_DATA} not found. Run: python separation/build_strict_fixtures.py"
        )
    expected = load_npz(TEST_DATA)
    params = strict_default_parameters()
    mc = run_motion_correction(VIDEO, params, mode="strict")
    sd = run_source_detection(mc.corrected_video, mc.imax, params, mode="strict")
    cf = run_component_filtering(
        roifn=sd.roifn,
        sigfn=sd.sigfn,
        seedsfn=sd.seedsfn,
        corrected_video=mc.corrected_video,
        params=params,
        datasmth=sd.datasmth,
        cutoff=sd.cutoff,
        pkcutoff=sd.pkcutoff,
        aux=sd.aux,
        mode="strict",
    )

    print(f"\nParameters: {params}")
    print(f"Input Signal shape: {cf.sigfn.shape}")

    result = run_calcium_deconvolution(
        sigfn=cf.sigfn,
        params=params,
        mode="strict",
    )

    checks = {
        "spkfn": (result.spkfn, expected["spkfn"]),
        "dff": (result.dff, expected["dff"]),
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

    print(f"\n{'=' * 60}")
    print(f"RESULT: {'SUCCESS' if all_pass else 'FAILURE'}")
    print(f"{'=' * 60}")
    return all_pass


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
