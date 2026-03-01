"""Intensity normalization helpers."""

from __future__ import annotations

from typing import Any

import numpy as np


def normalize(frame_in: Any | None = None, dim: Any | None = None) -> np.ndarray:
    """Normalize intensity to ``[0, 1]``.

    MATLAB source: ``utilities/elements/normalize.m``.
    """
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

    # MATLAB dimensions are 1-based.
    axis = int(dim) - 1 if int(dim) > 0 else int(dim)
    mn = np.nanmin(arr, axis=axis, keepdims=True)
    out = arr - mn
    mx = np.nanmax(out, axis=axis, keepdims=True)
    safe = np.where(mx == 0, 1.0, mx)
    out = out / safe
    out = np.where(mx == 0, 0.0, out)
    return out
