"""Shared utilities for calcium_deconvolution module."""
from __future__ import annotations
from typing import Any
import numpy as np

def default_parameters() -> dict[str, Any]:
    return {
        "Fsi": 20, "Fsi_new": 10, "spatialr": 0.5, "ttype": "single",
        "neuron_size": 5, "anidenoise_iter": 4, "anidenoise_dt": 1/7,
        "anidenoise_kappa": 0.5, "anidenoise_opt": 1, "anidenoise_ispara": 1,
        "bg_remove_ispara": 1, "mc_scl": 0.004, "mc_sigma_x": 5,
        "mc_sigma_f": 10, "mc_sigma_d": 1, "pix_select_sigthres": 0.8,
        "pix_select_corrthres": 0.6, "refine_roi_ispara": 1,
        "merge_roi_corrthres": 0.9,
    }

def sigmoid(x, a, c):
    if x is None or a is None or c is None:
        raise ValueError("x, a, and c are required")
    x_arr = np.asarray(x, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-float(a) * (x_arr - float(c))))
