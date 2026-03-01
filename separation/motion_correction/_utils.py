"""Shared utilities for motion_correction module.

These are self-contained copies of utility functions from the MIN1PIPE
pipeline, included here to satisfy the Island Rule (no external imports
from the parent codebase).
"""

from __future__ import annotations

from typing import Any

import numpy as np


def default_parameters() -> dict[str, Any]:
    """Return the default MIN1PIPE parameters."""
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


def normalize(frame_in, dim=None):
    """Normalize intensity to [0, 1]."""
    if frame_in is None:
        raise ValueError("frame_in must not be None")
    arr = np.asarray(frame_in, dtype=np.float64)
    if arr.size == 0:
        return arr
    if dim is None:
        dim = 4
    if int(dim) == 4:
        mn = np.nanmin(arr)
        out = arr - mn
        mx = np.nanmax(out)
        if mx == 0 or np.isnan(mx):
            return np.zeros_like(out)
        return out / mx
    axis = int(dim) - 1 if int(dim) > 0 else int(dim)
    mn = np.nanmin(arr, axis=axis, keepdims=True)
    out = arr - mn
    mx = np.nanmax(out, axis=axis, keepdims=True)
    safe = np.where(mx == 0, 1.0, mx)
    out = out / safe
    out = np.where(mx == 0, 0.0, out)
    return out
