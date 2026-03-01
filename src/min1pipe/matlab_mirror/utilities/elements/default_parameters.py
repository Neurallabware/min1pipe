"""Default MIN1PIPE parameters."""

from __future__ import annotations

from typing import Any


def default_parameters() -> dict[str, Any]:
    """Return the default MIN1PIPE parameters.

    MATLAB source: ``utilities/elements/default_parameters.m``.
    """
    return {
        "Fsi": 20,
        "Fsi_new": 10,
        "spatialr": 0.5,
        "ttype": "single",
        "neuron_size": 5,
        "anidenoise_iter": 4,
        "anidenoise_dt": 1 / 7,
        "anidenoise_kappa": 0.5,
        "anidenoise_opt": 1,
        "anidenoise_ispara": 1,
        "bg_remove_ispara": 1,
        "mc_scl": 0.004,
        "mc_sigma_x": 5,
        "mc_sigma_f": 10,
        "mc_sigma_d": 1,
        "pix_select_sigthres": 0.8,
        "pix_select_corrthres": 0.6,
        "refine_roi_ispara": 1,
        "merge_roi_corrthres": 0.9,
    }
