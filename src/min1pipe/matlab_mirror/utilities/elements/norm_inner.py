"""Normalized inner-product helper."""

from __future__ import annotations

from typing import Any

import numpy as np


def norm_inner(a: Any | None = None, b: Any | None = None) -> np.ndarray:
    """Compute normalized inner product ``a @ b / (||a|| * ||b||)``.

    MATLAB source: ``utilities/elements/norm_inner.m``.
    """
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
