"""Shared utilities for source_detection module."""
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


def normalize(frame_in, dim=None):
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


def norm_inner(a, b):
    if a is None or b is None:
        raise ValueError("a and b are required")
    a_arr = np.asarray(a, dtype=np.float64)
    b_arr = np.asarray(b, dtype=np.float64)
    num = a_arr @ b_arr
    a_norm = np.sqrt(np.sum(a_arr**2, axis=1, keepdims=True))
    b_norm = np.sqrt(np.sum(b_arr**2, axis=0, keepdims=True))
    den = a_norm @ b_norm
    out = np.zeros_like(num, dtype=np.float64)
    np.divide(num, den, out=out, where=den != 0)
    return out


def sigmoid(x, a, c):
    if x is None or a is None or c is None:
        raise ValueError("x, a, and c are required")
    x_arr = np.asarray(x, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-float(a) * (x_arr - float(c))))
